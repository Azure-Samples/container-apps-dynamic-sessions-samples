# Session lifecycle configuration

This guide explains how to configure the lifecycle behavior of sessions in your session pool.

## Overview

When creating a session pool, you can configure how sessions are managed through `properties.dynamicPoolConfiguration.lifecycleConfiguration`. This allows you to control when sessions are automatically terminated.

For the full API specification, see the [SessionPools API spec](https://learn.microsoft.com/en-us/rest/api/resource-manager/containerapps/container-apps-session-pools/create-or-update?view=rest-resource-manager-containerapps-2025-07-01&tabs=HTTP).

## Lifecycle types

Starting from API version `2025-01-01`, you can choose one of two lifecycle types for your sessions.

### Timed

With the `Timed` lifecycle, a session is automatically deleted after a period of inactivity.

```json
{
  "dynamicPoolConfiguration": {
    "lifecycleConfiguration": {
      "cooldownPeriodInSeconds": 600,
      "lifecycleType": "Timed"
    }
  }
}
```

| Property                   | Description                                                          |
| -------------------------- | -------------------------------------------------------------------- |
| `cooldownPeriodInSeconds`  | The session is deleted when there are no requests for this duration |
| `maxAlivePeriodInSeconds`  | Not supported for `Timed` lifecycle                                  |

Any request sent to a session resets the cooldown timer, extending the session's time-to-live by `cooldownPeriodInSeconds`.

> [!NOTE]
> This is the default behavior and works the same as `ExecutionType: Timed` in previous API versions. It is supported for all session pool types.

### OnContainerExit

With the `OnContainerExit` lifecycle, a session remains active until the container exits on its own or reaches the maximum alive period.

```json
{
  "dynamicPoolConfiguration": {
    "lifecycleConfiguration": {
      "maxAlivePeriodInSeconds": 6000,
      "lifecycleType": "OnContainerExit"
    }
  }
}
```

| Property                   | Description                                                 |
| -------------------------- | ----------------------------------------------------------- |
| `maxAlivePeriodInSeconds`  | Maximum time the session can stay alive before being deleted |
| `cooldownPeriodInSeconds`  | Not supported for `OnContainerExit` lifecycle               |

The session will be deleted when either:

- The session container exits on its own
- The session has been alive for longer than `maxAlivePeriodInSeconds`

> [!NOTE]
> This lifecycle type is only supported in **Custom Container Session Pools**.

## Next steps

- [Create a custom container session pool](../code-interpreter/bring-your-own-code-interpreter/tutorials/python-custom-container-tutorial.md)
- [Container probes for session pools](container-probes.md)
- [Stop a session](stop-session.md)
