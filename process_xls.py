import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import sys

pd.options.mode.chained_assignment = None

# require a command line argument
xlspath = sys.argv[1]

# Oregon publishes them as excel spreadsheet
finances = pd.read_excel(xlspath)

# comes from Oregon's published ORESTAR reporting guide
# 1 indicates income, -1 indicates spending
transaction_t = {
    'Cash Contribution': 1,
    'In-Kind Contribution': 1,
    'In-Kind Personal Expenditure': 1,
    'Forgiven Personal Expenditures': 1,
    'In-Kind Account Payable': 1,
    'Forgiveen Account Payable': 1,
    'Items Sold at Fair Market Value': 1,
    'Loan Received': 1,
    'Lost or Returned Check': 1,
    'Refunds or Rebates': 1,
    'Miscellaneous Other Receipt': 1,
    'Cash Expenditure': -1,
    'Personal Expenditure for Reimbursement': -1,
    'Account Payable': -1,
    'Loan Payment': -1,
    'Return or Refund of Contribution': -1,
    'Miscellaneous Other Disbursement': -1
}

# Used to keep track of funding by income type
funding_composition = {}
funding_percentages = {}

# record untracked types of exchanges
untracked = {}

# keep track of income and spending over time
start_date = pd.to_datetime(finances['Tran Date'].min())
end_date = pd.to_datetime(finances['Tran Date'].max())
timeline = np.arange(start_date, end_date, dtype="datetime64[D]")
income_dt = np.zeros(timeline.size)
spending_dt = np.zeros(timeline.size)

# running totals
cash_on_hand = 0
total_funds_received = 0

# iterate over all rows and compute values
for i, row in finances.iterrows():
    t, n = row['Sub Type'], row['Amount']
    d = pd.to_datetime(row['Tran Date'])
    dateidx = np.where(timeline == d)[0]

    # tracked transaction type
    if t in transaction_t:
        cash_on_hand += transaction_t[t]*n

        if transaction_t[t] == 1: # income
            total_funds_received += n
            income_dt[dateidx] += n
            if t in funding_composition:
                funding_composition[t] += n
            else:
                funding_composition[t] = n
        else: # spending
            spending_dt[dateidx] += n
    else: # untracked type of transaction
        if t in untracked:
            untracked[t] += 1
        else:
            untracked[t] = 1
    
for key, value in funding_composition.items():
    funding_percentages[key] = 100*(value / total_funds_received)

scaled_income_dt = income_dt / 1000
scaled_spending_dt = spending_dt / 1000

# plot income and spending over time
plt.plot(timeline, scaled_income_dt, label='income')
plt.plot(timeline, scaled_spending_dt, label='spending', color='red')

plt.title("Income and spending per day")
plt.xlabel('Date')
plt.ylabel('Dollars per day (thousands)')
plt.xticks(rotation=30, ha='right')
plt.legend()

plt.show()