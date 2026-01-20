# View logs for custom container session pools

This guide explains how to access and view logs for your custom container session pools in Azure Container Apps dynamic sessions.

## Prerequisites

- An Azure Container Apps environment with a custom container session pool
- An Azure Log Analytics workspace (or you can create one during setup)

## Configure logging

### Step 1: Enable Azure Monitor logging

1. Navigate to your **Container Apps Environment** in the Azure portal
2. Under **Monitoring**, select **logging options**
3. Set the logs destination to **Azure Monitor**

### Step 2: Configure diagnostic settings

1. In your Container Apps Environment, navigate to the **Diagnostic settings** blade under **Monitoring**
2. Select **+ Add diagnostic setting**
3. Provide a name for your diagnostic setting
4. Under **Logs**, select the session-related log categories you want to capture
5. Under **Destination details**, select **Send to Log Analytics workspace**
6. Choose your target Log Analytics workspace (or create a new one)
7. Select **Save**

## View session logs

Once diagnostic settings are configured, logs will be sent to your Log Analytics workspace. You can query the following tables to view session-related logs:

| Table name | Description |
| ---------- | ----------- |
| `AppEnvSessionConsoleLogs` | Console output and logs from your session containers |
| `AppEnvSessionLifecycleLogs` | System logs for session allocation events |
| `AppEnvSessionPoolEvents` | Events related to the session pool management, pod creation, deletion, etc. |

### Query logs in Log Analytics

1. Navigate to your **Log Analytics workspace** in the Azure portal
2. Select **Logs** under **General**
3. Use Kusto Query Language (KQL) to query the session logs

#### Example queries

**View recent console logs from sessions:**

```kusto
AppEnvSessionConsoleLogs
| where TimeGenerated > ago(1h)
| order by TimeGenerated desc
| take 100
```

**View session lifecycle events:**

```kusto
AppEnvSessionLifecycleLogs
| where TimeGenerated > ago(1h)
| order by TimeGenerated desc
```

**View session pool events:**

```kusto
AppEnvSessionPoolEvents
| where TimeGenerated > ago(1h)
| order by TimeGenerated desc
```
