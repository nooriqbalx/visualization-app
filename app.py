import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import seaborn as sns

df = pd.read_excel("Enhanced_Dummy_HBL_Data.xlsx")

st.set_page_config(page_title="HBL Transactions Dashboard", layout="wide")
st.title("HBL Transactions Dashboard")

st.write("""
### How to Use:
- Use the filters in the sidebar to dynamically explore the dataset.
- Each chart updates automatically based on the selected filters.
""")

st.sidebar.header("Filters")
regions = st.sidebar.multiselect("Select Region(s)", options=df["Region"].unique(), default=df["Region"].unique())
account_types = st.sidebar.multiselect("Select Account Type(s)", options=df["Account Type"].unique(), default=df["Account Type"].unique())

filtered_df = df[df["Region"].isin(regions) & df["Account Type"].isin(account_types)]

st.subheader("Account Type Distribution")
account_type_counts = filtered_df["Account Type"].value_counts()
fig1 = px.pie(values=account_type_counts.values, names=account_type_counts.index, title="Account Type Distribution")
st.plotly_chart(fig1, use_container_width=True)

st.subheader("Transaction Flow by Beneficiary Bank")
transaction_flow = filtered_df.groupby(["Region", "Transaction To"])["Credit"].sum().reset_index()
top_banks_per_region = transaction_flow.groupby("Region").apply(lambda x: x.nlargest(5, "Credit")).reset_index(drop=True)
fig2 = px.bar(top_banks_per_region, x="Transaction To", y="Credit", color="Region", 
              title="Top 5 Beneficiary Banks by Region", barmode="group")
st.plotly_chart(fig2, use_container_width=True)

st.subheader("Geographic Heatmap of Transactions")
transaction_intensity = filtered_df.groupby("Region")[["Credit", "Debit"]].sum().reset_index()
fig3 = px.density_heatmap(transaction_intensity, x="Region", y="Credit", z="Debit",
                          title="Transaction Intensity by Region", color_continuous_scale="Viridis")
st.plotly_chart(fig3, use_container_width=True)


st.subheader("Anomalies in Transactions")
from scipy.stats import zscore
filtered_df["Credit Z-Score"] = zscore(filtered_df["Credit"])
filtered_df["Debit Z-Score"] = zscore(filtered_df["Debit"])
anomalies = filtered_df[(abs(filtered_df["Credit Z-Score"]) > 3) | (abs(filtered_df["Debit Z-Score"]) > 3)]
fig4 = px.scatter(anomalies, x="Credit", y="Debit", color="Region", title="Anomalies in Transactions")
st.plotly_chart(fig4, use_container_width=True)

st.subheader("Comparative Analysis of Transaction Types")
fig5 = px.box(filtered_df, x="Account Type", y="Credit", color="Account Type", title="Credit Transactions by Account Type")
fig6 = px.box(filtered_df, x="Account Type", y="Debit", color="Account Type", title="Debit Transactions by Account Type")
st.plotly_chart(fig5, use_container_width=True)
st.plotly_chart(fig6, use_container_width=True)

st.subheader("Customer Insights")
if "Customer Type Description" in filtered_df.columns:
    customer_insights = filtered_df.groupby("Customer Type Description")["Credit", "Debit"].sum().reset_index()
    fig7 = px.bar(customer_insights, x="Customer Type Description", y=["Credit", "Debit"], 
                  title="Total Credit and Debit Amounts by Customer Type", barmode="stack")
    st.plotly_chart(fig7, use_container_width=True)
else:
    st.warning("Customer Type Description column not available in the dataset.")

sns.set(style="darkgrid", palette="deep")
st.subheader("Correlation Analysis")
numeric_cols = df.select_dtypes(include=['float64', 'int64'])
correlation_matrix = numeric_cols.corr()

plt.figure(figsize=(10, 8))
sns.heatmap(correlation_matrix, annot=True, fmt=".2f", cmap="coolwarm")
plt.title("Correlation Matrix of Numeric Variables")
st.pyplot(plt) 

st.subheader("Transaction Amount Distribution: Credit vs Debit")
sns.set(style="whitegrid")
plt.figure(figsize=(14, 6), facecolor='black')

plt.subplot(1, 2, 1) 
sns.histplot(filtered_df['Credit'], kde=True, color='blue', bins=30)
plt.title('Credit Transaction Distribution')
plt.xlabel('Credit Amount')
plt.ylabel('Frequency')

plt.subplot(1, 2, 2)  
sns.histplot(filtered_df['Debit'], kde=True, color='red', bins=30)
plt.title('Debit Transaction Distribution')
plt.xlabel('Debit Amount')
plt.ylabel('Frequency')

plt.tight_layout()
st.pyplot(plt) 
