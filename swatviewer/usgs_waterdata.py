import pandas as pd



def read_usgs_rdb(filepath_or_link, verbose=False):
    if verbose:
        print(f'download link is: "{filepath_or_link}".')

    df = pd.read_table(filepath_or_link, comment='#', header=0)

    # if df.shape[0] <= 1:
    #     if verbose:
    #         print('The link retrieved empty record.')
    #     return df[:0]

    # first row is data type
    df2 = df[1:]
    for i, s in df.iloc[0].iteritems():
        if i == 'datetime':
            s = 'd'
        if s.endswith('d'):
            try:
                df2.loc[:, i] = pd.DatetimeIndex(df2.loc[:, i])
            except:
                print('Unknown datetime format for column ' + df.columns[i])
        if s.endswith('n'):
                df2.loc[:, i] = pd.to_numeric(df2.loc[:, i], errors='ignore')
    return df2

def translate_gage_site_no(site_ids):
    sites = site_ids if isinstance(site_ids, list) else list(site_ids)
    return [
        ('0000000' + str(s))[-8:] for s in sites
    ]

def read_usgs_streamflow_stage(site_ids, begin_date='2000-01-01', end_date=None, flow=True, stage=False):


    begin_date = pd.Timestamp(begin_date)

    link  = f'https://waterdata.usgs.gov/nwis/dv?format=rdb&begin_date={begin_date:%Y-%m-%d}'

    # print(site_ids, type(site_ids))
    site_ids = '&site_no={}'.format('&site_no='.join(translate_gage_site_no(site_ids)))

    flow  = '&cb_00060=on' if flow else ''
    stage = '&cb_00065=on' if stage else ''
    end_date = f'&end_date={pd.Timestamp(end_date):%Y-%m-%d}' if end_date else ''

    df = read_usgs_rdb(link + end_date + site_ids + flow + stage, )

    df = df.set_index('datetime')

    to_drop = df.columns[:1].to_list()
    cols = []
    for c in df.columns[1:]:
        if c.lower() == 'site_no':
            cols.append(c)
            continue

        if c.lower().endswith('cd'):
            to_drop.append(c)
            continue

        c = c.lstrip(c.split('_')[0])
        c = c.replace('_00060', 'Discharge')
        c = c.replace('_00065', 'Stage')
        c = c.replace('_00001', ' Maximum')
        c = c.replace('_00002', ' Minimum')
        c = c.replace('_00003', ' Mean')

        cols.append(c)

    df.drop(to_drop, axis=1, inplace=True)
    df.columns = cols

    if df.shape[1] == 1:
        df['Discharge Mean'] = pd.NA

    return df




