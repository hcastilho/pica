#! /usr/bin/env python

import yaml
from  datetime import date, datetime, timedelta
import os
from operator import itemgetter

import click

MIN_PERIOD = timedelta(minutes=10)
TOTAL_HEADER = """
  -----------------------
 |     Day    |   Total  |
  ----------------------- """
TOTAL_ROW = ' | {} | {}  |'
TOTAL_FOOTER = '  ----------------------- '

TABLE_HEADER = """
  ---------------------------------- ---------
 |     Day    |    In    |    Out   |  Total  |
  ---------------------------------- --------- """
TABLE_ROW_A = ' | {0} | {1} | {2} | {3} |'
TABLE_ROW_B = ' |            | {1} | {2} | {3} |'
TABLE_FOOTER = '  -------------------------------------------- '

class Context():
    def __init__(self, file):
        self.file = file

passctx = click.make_pass_decorator(Context)


@click.group()
@click.option('--file', default=os.path.expanduser('~/dev/pica/time.yaml'), show_default=True)
@click.pass_context
def main(ctx, file):
    ctx.obj = Context(file)


#@main.command('tik')
@main.command()
@passctx
def tik(ctx):
    print('tik')
    timetable = read_timetable(ctx)
    latest = get_latest_day(timetable)
    period = get_latest_period(latest['table'])
    key = 'out' if 'in' in period else 'in'
    now = datetime.now().time().strftime('%H:%M:%S')

    # If out of the computer for less man MIN_PERIOD remove entries
    if key == 'in':
        try:
            # if in we added a new enty in get_latest_period so -2
            # and we need to do more manipulation on the timetable
            # the code needs to be changed to make manipulation easier
            previous = latest['table'][-2]
            last_out = previous['out']
            interval = calc_length({'in': last_out, 'out': now})
        except (KeyError, IndexError):
            interval = None
        if interval and interval < MIN_PERIOD:
            print('Interval of {} is less then {} min'.format(
                interval.seconds/60,
                MIN_PERIOD.seconds/60,
            ))
            del previous['out']
            latest['table'].remove(period)
            write_timetable(ctx, timetable)
            return

    period[key] = now
    print('{}: {}'.format(key, now))
    write_timetable(ctx, timetable)


@main.command()
@passctx
def show(ctx):
    timetable = read_timetable(ctx)
    print(TOTAL_HEADER)
    for day in timetable:
        worktime = timedelta()
        for period in day['table']:
            worktime = worktime + calc_length(period)
        print(TOTAL_ROW.format(day['date'], str(worktime)))
    print(TOTAL_FOOTER)


def calc_length(period):
    times = {}
    for key in ('in', 'out'):
        if key in period:
            times[key] = datetime.combine(
                date.today(),    # Justs for calculations
                datetime.strptime(period[key], '%H:%M:%S').time()
            )
        else:
            times[key] = datetime.now()
    diff = (times['out'] - times['in'])
    diff = timedelta(seconds=diff.seconds)
    return diff


@main.command()
@passctx
def table(ctx):
    timetable = read_timetable(ctx)
    print(TABLE_HEADER)
    for day in timetable:
        for i, period in enumerate(day['table']):
            row = TABLE_ROW_A if i == 0 else TABLE_ROW_B
            print(row.format(
                day['date'],
                period['in'],
                period['out'] if 'out' in period else '        ',
                str(calc_length(period))
            ))
        print(TABLE_FOOTER)


def get_latest_day(timetable):
    # Empty timetable or last entry not today
    today = date.today()
    if not timetable or today != timetable[0]['date']:
        latest = {'date': today, 'table': []}
        timetable.insert(0, latest)
    else:
        latest = timetable[0]
    return latest


# TODO get_latest_period should not alter structure
def get_latest_period(periods):
    if not periods or 'out' in periods[-1]:
        period = {}
        periods.append(period)
    else:
        period = periods[-1] # latest
    return period


def read_timetable(ctx):
    try:
        with open(ctx.file) as handle:
            timetable = yaml.load(handle.read())
    except FileNotFoundError:
        timetable = []
    else:
        # Days sorted latest first
        timetable = sorted(timetable, key=itemgetter('date'), reverse=True)

    # Periods sorted earliest first
    for day in timetable:
        day['table'] = sorted(day['table'], key=itemgetter('in'))
    return timetable


def write_timetable(ctx, timetable):
    with open(ctx.file, 'w') as handle:
        handle.write(yaml.dump(timetable))


def next_tik_type():
    ctx=Context(os.path.expanduser('~/dev/pica/time.yaml'))
    timetable = read_timetable(ctx)
    latest = get_latest_day(timetable)
    period = get_latest_period(latest['table'])
    return 'out' if 'in' in period else 'in'


if __name__ == '__main__':
    main()
