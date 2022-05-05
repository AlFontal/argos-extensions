import pytz
import base64
import requests

import pandas as pd
import plotnine as p9

from datetime import datetime, timedelta
from mizani.formatters import date_format

# Specify personal Nightscout site, number of hours to plot, and timezone
NIGHTSCOUT_SITE = 'cgm-monitor-alfontal.herokuapp.com'
N_HOURS = 4
TIMEZONE = pytz.timezone('CET')
directions = {
    'DoubleDown': '⇊',
    'SingleDown': '↓',
    'FortyFiveDown': '↘',
    'Flat': '→',
    'FortyFiveUp': '↗',
    'SingleUp': '↑',
    'DoubleUp': '⇈'
}

prev_time = datetime.now(tz=pytz.timezone('UTC')) - timedelta(hours=N_HOURS)
current_url = f'https://{NIGHTSCOUT_SITE}/api/v1/entries/sgv.json?&find[dateString][$gte]={prev_time}&count=100'

current_df = (pd.DataFrame(requests.get(current_url.replace(' ', 'T')).json())
            .assign(date=lambda dd: pd.to_datetime(dd.dateString).dt.tz_convert(TIMEZONE))
            .assign(device=lambda dd: dd.device.str.split('-').str[0])
            [['date', 'sgv', 'device', 'direction']]
    )

last_device = current_df.device.iloc[0]
last_value = current_df.iloc[0]
previous_value = current_df.query(f'device=="{last_device}"').iloc[1]
last_glucose = last_value['sgv']
delta = last_glucose - previous_value['sgv']
direction = directions[last_value['direction']]
sign = '+' if delta >= 0 else ''
minutes_since_previous = (last_value['date'] - previous_value['date']).total_seconds() / 60
delta_per_min = round(delta / minutes_since_previous, 1)

p = (current_df
     .pipe(lambda df: p9.ggplot(df)
                      + p9.aes('date', 'sgv')
                      + p9.geom_point(size=1)
                      + p9.geom_line(p9.aes(group='device'))
                      + p9.theme_bw()
                      + p9.labs(x='', y='Glucose [mg/dl]')
                      + p9.scale_x_datetime(labels=date_format('%H:%M', tz=TIMEZONE))
                      + p9.theme(dpi=120, figure_size=(5, 2.5))
                      + p9.geom_hline(yintercept=70, linetype='dashed', color='green')
                      + p9.geom_hline(yintercept=150, linetype='dashed', color='green')
                      + p9.ylim(min(40, df.sgv.min()), max(200, df.sgv.max() + 10))
           )
     )

if current_df.device.nunique() > 1:
    last_values_per_device = (current_df
                              .groupby('device')
                              .apply(lambda dd: dd.sort_values('date').iloc[-1])
                              .reset_index(drop=True)
                              .assign(date=lambda dd: dd.date + pd.to_timedelta(('15 min')))
                              )
    p += p9.geom_text(p9.aes(label='device.str.split("-").str[0]'),
                      data=last_values_per_device, ha='center', size=8,
                      adjust_text=dict(expand_points=(0, 2), arrowprops=dict(arrowstyle='-', color='white')))

p.save('last_plot.png')

td = datetime.now(tz=TIMEZONE) - last_value['date']

with open('last_plot.png', "rb") as image_file:
    b64_image = base64.b64encode(image_file.read()).decode()

print(f'{last_glucose} ({sign}{delta_per_min}) {direction} ({round(td.seconds / 60)}m)')
print('---')
print(f' |image={b64_image} href=https://{NIGHTSCOUT_SITE}')
