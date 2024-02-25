import pandas as pd
import numpy as np
import math

import hvplot as hv
import panel as pn
import hvplot.pandas

pn.extension('bokeh', template='bootstrap')

def simulate(initialcapital , bet_chance , betsize , rewardrisk, riskpercent, max_rounds, max_profit , num_realization):
  hv.extension('bokeh')

  bet = lambda cash: cash * (betsize/100)

  all_profits = []
  for i in range(0, num_realization):
      profits = []
      cash = initialcapital
      for i in range(0, max_rounds):
          if cash <= 1: # went blowout
              break

          if cash >= max_profit:
              break

          bet_value = bet(cash)
          if np.random.rand() < (bet_chance/100):
              cash += bet_value *rewardrisk * (riskpercent/100) #*.1
          else:
              cash -= bet_value *(riskpercent/100) #* .05

          profits.append(cash)

      all_profits.append(profits)
  df = pd.DataFrame(all_profits).T
  plot1 =  df.hvplot.line( logy=True, height=600, width=1200).opts(show_grid=True, ylabel='Profit', xlabel='Bet')

  bust = [ x for x in all_profits if x[-1] <= 1 ]
  rich = [ x for x in all_profits if x[-1] >= max_profit ]
  text = f"""### Result of Simulation for {num_realization} Realization:
             Blowout Accounts: {round(len(bust) / len(all_profits) * 100)} %
             Avg time to go Blowout: {np.mean([ len(x) for x in bust ]):.1f}
             Reach Max profit: {round(len(rich) / len(all_profits) * 100):.1f} %
             Avg time to reach max profit:, {np.mean([ len(x) for x in rich ]):.1f}
             Challenge from {initialcapital}$ to {max_profit}$
             intial bet {betsize*initialcapital/100}$ with winrate={bet_chance}% reward to risk={rewardrisk} and possible reward/loss={riskpercent/100*betsize*initialcapital/100}
          """
  if round(len(bust) / len(all_profits)) > .5:
    alert_type="danger"
  else:
    alert_type="success"
  return pn.Column(plot1, pn.pane.Alert(text, alert_type=alert_type, height=150, width=1200, sizing_mode="fixed"))

initialcapital = pn.widgets.IntSlider(name='Initial Capital', start=1000, end=100000, step=1000, value=2000)
bet_chance = pn.widgets.FloatSlider(name='Win Rate %', start=0, end=100, step=0.1, value=60.0)
betsize = pn.widgets.FloatSlider(name='Bet Size %', start=0, end=100.0, step=1, value=50)
rewardrisk = pn.widgets.FloatSlider(name='Reward:Risk', start=0, end=0.1, step=1, value=1.0)
riskpercent = pn.widgets.FloatSlider(name='Risk %', start=0, end=100.0, step=1, value=100.0)
max_rounds = pn.widgets.IntSlider(name='Max Rounds', start=1000, end=10000, step=1000, value=1000)
max_profit = pn.widgets.IntSlider(name='Max Profit', start=10000, end=10000000, step=1000, value=1000000)
num_realization = pn.widgets.IntSlider(name='Number of Realization', start=100, end=10000, step=100, value=100)
selectedmethod = pn.widgets.Select(name='Select Method', value='Mean', options=['Full Kelly Criterion' , 'Half Kelly Criterion' , 'Fractional Kelly Criterion','Constant Proportion Betting','Martingale Betting System'])

bound_plot = pn.bind(simulate, initialcapital= initialcapital, bet_chance =bet_chance , betsize=betsize , rewardrisk=rewardrisk, riskpercent=riskpercent, max_rounds=max_rounds, max_profit=max_profit , num_realization=num_realization)

pn.Row(pn.Column(initialcapital, bet_chance, betsize, rewardrisk, riskpercent, max_rounds, max_profit, num_realization,selectedmethod),bound_plot).servable(title="Bet Size Optimizer - Simulation Account Growth")

