#!/usr/bin/env python3
"""Supervisor for the BASE_CENSUS collector.

First start: pins launch head H (base-rpc.publicnode.com eth_blockNumber) and writes state/config.json:
  config.json may also list extra_streams [{name: bf3, start, end}, ...] (same endpoints as bf2), used to move part of
  the remaining bf range off drpc.
  bf range = [H - BACKFILL_BLOCKS, H - HEAD_LAG]   (base.drpc.org); if config has bf_split_end/bf2_start the upper
             part [bf2_start, H - HEAD_LAG] is done by stream bf2 (gateway.tenderly.co/public/base, fallback base.meowrpc.com)
  fw range = [H - HEAD_LAG + 1, stop_block]        (base-rpc.publicnode.com, fallback base.drpc.org)
  fw stop  = when (V4LIVE.DONE|FAILED) AND (SHALLOW_LIVE.DONE|FAILED) exist in the sentinel dir, or launch + 7 h,
             whichever first; stop_block = head at detection - HEAD_LAG + STOP_MARGIN_BLOCKS.
Runs census.py --stream bf and --stream fw as child processes (restarted on non-zero exit, resume from checkpoint),
then gap-fill (census.py --stream gf) for blocks listed in gaps.csv, then finalize.py, then writes the sentinel.
Re-running supervisor.py resumes (config.json is kept).
Env at first start: BACKFILL_BLOCKS (default 10800), BF2_BLOCKS (default 0; the 2026-09-30 run used the equivalent of 6400,
set by editing config.json 10 minutes after launch).
"""
import json, os, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
STATE = os.path.join(HERE, 'state')
OUTDIR = os.path.abspath(os.path.join(HERE, '..'))
SENT = '/home/user/dapparb/research-material/.sentinels'
NAME = 'BASE_CENSUS'
BACKFILL_BLOCKS = int(os.environ.get('BACKFILL_BLOCKS', '10800'))
HEAD_LAG = 10
STOP_MARGIN_BLOCKS = 150
MAX_FOLLOW_SECONDS = 7 * 3600
MAX_RESTARTS = 200


def utcnow():
    return time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())


def log(*a):
    print(utcnow(), *a, flush=True)


def head():
    import requests
    for url in ('https://base-rpc.publicnode.com', 'https://base.drpc.org'):
        for _ in range(5):
            try:
                r = requests.post(url, json={'jsonrpc': '2.0', 'id': 1, 'method': 'eth_blockNumber', 'params': []},
                                  headers={'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) Chrome/124.0'}, timeout=20)
                return int(r.json()['result'], 16), url
            except Exception as e:
                log('head error', url, e); time.sleep(3)
    raise RuntimeError('cannot get head')


def save_json(p, obj):
    with open(p + '.tmp', 'w') as f:
        json.dump(obj, f, indent=1, sort_keys=True)
    os.replace(p + '.tmp', p)


def ckpt(stream):
    p = os.path.join(STATE, '%s.ckpt.json' % stream)
    if os.path.exists(p):
        with open(p) as f:
            return json.load(f)
    return {}


class Child:
    def __init__(self, stream, args):
        self.stream, self.args, self.p, self.restarts = stream, args, None, 0

    def start(self):
        lf = open(os.path.join(HERE, 'census_%s.log' % self.stream), 'a')
        self.p = subprocess.Popen([sys.executable, '-u', os.path.join(HERE, 'census.py'), '--stream', self.stream] + self.args,
                                  cwd=HERE, stdout=lf, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL)
        log('started', self.stream, 'pid', self.p.pid, self.args)

    def poll(self):
        """True when finished for good."""
        if self.p is None:
            self.start(); return False
        rc = self.p.poll()
        if rc is None:
            return False
        if ckpt(self.stream).get('done'):
            log(self.stream, 'finished rc', rc); return True
        self.restarts += 1
        log(self.stream, 'exited rc', rc, 'restart', self.restarts)
        if self.restarts > MAX_RESTARTS:
            raise RuntimeError('%s exceeded %d restarts' % (self.stream, MAX_RESTARTS))
        time.sleep(30)
        self.start()
        return False


def main():
    os.makedirs(STATE, exist_ok=True)
    cp = os.path.join(STATE, 'config.json')
    cfg = {}
    if os.path.exists(cp):
        with open(cp) as f:
            cfg = json.load(f)
    if 'launch_head' not in cfg:
        h, url = head()
        now = time.time()
        cfg = {
            'launch_unix': now, 'launch_utc': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(now)), 'launch_head': h, 'launch_head_source': url,
            'backfill_blocks': BACKFILL_BLOCKS, 'head_lag': HEAD_LAG, 'stop_margin_blocks': STOP_MARGIN_BLOCKS,
            'max_follow_seconds': MAX_FOLLOW_SECONDS, 'sentinel_dir': SENT,
            'bf_start': h - BACKFILL_BLOCKS, 'bf_end': h - HEAD_LAG, 'fw_start': h - HEAD_LAG + 1,
        }
        bf2 = int(os.environ.get('BF2_BLOCKS', '0'))
        if bf2 > 0:
            cfg['bf_split_end'] = cfg['bf_end'] - bf2
            cfg['bf2_start'] = cfg['bf_split_end'] + 1
        save_json(cp, cfg)
        log('pinned config', cfg)
    else:
        log('resuming with config', cfg)
    try:
        kids = [Child('bf', ['--start', str(cfg['bf_start']), '--end', str(cfg.get('bf_split_end', cfg['bf_end'])), '--chunk', '40', '--workers', '3']),
                Child('fw', ['--start', str(cfg['fw_start']), '--chunk', '30', '--workers', '2'])]
        if cfg.get('bf2_start'):
            kids.append(Child('bf2', ['--start', str(cfg['bf2_start']), '--end', str(cfg.get('bf2_end', cfg['bf_end'])), '--chunk', '40', '--workers', '3']))
        for x in cfg.get('extra_streams', []):
            kids.append(Child(x['name'], ['--start', str(x['start']), '--end', str(x['end']), '--chunk', '40', '--workers', '3']))
        pending = list(kids)
        while pending:
            pending = [k for k in pending if not k.poll()]
            time.sleep(10)
        # gap fill
        gaps_p = os.path.join(OUTDIR, 'gaps.csv')
        if os.path.exists(gaps_p) and not ckpt('gf').get('done'):
            import csv
            with open(gaps_p) as f:
                nums = sorted({int(r['block_number']) for r in csv.DictReader(f) if r['stream'] != 'gf'})
            if nums:
                bfp = os.path.join(STATE, 'gf_blocks.txt')
                if not os.path.exists(bfp):
                    with open(bfp, 'w') as f:
                        f.write('\n'.join(map(str, nums)) + '\n')
                g = Child('gf', ['--blocks-file', bfp, '--chunk', '10', '--workers', '2'])
                while not g.poll():
                    time.sleep(10)
        rc = subprocess.call([sys.executable, '-u', os.path.join(HERE, 'finalize.py')], cwd=HERE)
        if rc != 0:
            raise RuntimeError('finalize.py rc %d' % rc)
        with open(os.path.join(STATE, 'finalize_summary.json')) as f:
            summ = json.load(f)
        with open(os.path.join(SENT, NAME + '.DONE'), 'w') as f:
            json.dump({'finished_utc': utcnow(), 'outdir': OUTDIR, 'summary': summ}, f, indent=1)
        log('wrote sentinel DONE')
    except Exception as e:
        log('FAILED', repr(e))
        with open(os.path.join(SENT, NAME + '.FAILED'), 'w') as f:
            f.write('%s supervisor failed: %r\n' % (utcnow(), e))
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
