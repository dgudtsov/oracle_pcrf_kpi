# PCRF Graph Metric Suggestions (from CSV headers)

## Suggested Panels

### Diameter Errors

- `DiameterTooBusyReceived` from `ProtocolErrorStats-*.csv` grouped by `PolicyServer`
- `DiameterTooBusySent` from `ProtocolErrorStats-*.csv` grouped by `PolicyServer`
- `DiameterUnableToDeliverReceived` from `ProtocolErrorStats-*.csv` grouped by `PolicyServer`
- `DiameterUnableToDeliverSent` from `ProtocolErrorStats-*.csv` grouped by `PolicyServer`
- `DiameterUnknownSessionIdReceived` from `ProtocolErrorStats-*.csv` grouped by `PolicyServer`
- `DiameterUnknownSessionIdSent` from `ProtocolErrorStats-*.csv` grouped by `PolicyServer`
- `DiameterUnableToComplyReceived` from `ProtocolErrorStats-*.csv` grouped by `PolicyServer`
- `DiameterUnableToComplySent` from `ProtocolErrorStats-*.csv` grouped by `PolicyServer`

### Gx/PCEF TPS

- `PcefCCRICurrentTPS` from `TpsStats-*.csv` grouped by `PolicyServer` (CCR-I)
- `PcefCCRIMaxTPS` from `TpsStats-*.csv` grouped by `PolicyServer` (CCR-I)
- `PcefCCRUCurrentTPS` from `TpsStats-*.csv` grouped by `PolicyServer` (CCR-U)
- `PcefCCRTCurrentTPS` from `TpsStats-*.csv` grouped by `PolicyServer` (CCR-T)
- `PcefRARCurrentTPS` from `TpsStats-*.csv` grouped by `PolicyServer` (RAR)
- `PcefGxSummaryCurrentTPS` from `TpsStats-*.csv` grouped by `PolicyServer` (calculated as `PcefCCRICurrentTPS+PcefCCRUCurrentTPS+PcefCCRTCurrentTPS+PcefRARCurrentTPS`)
- `PcefGxSummaryMaxTPS` from `TpsStats-*.csv` grouped by `PolicyServer` (calculated as `PcefCCRIMaxTPS+PcefCCRUCurrentTPS+PcefCCRTCurrentTPS+PcefRARCurrentTPS`)

### MPE Overview

- `MaxTransactionsPerSecond` from `KpiStats-*.csv` grouped by `PolicyServer` (Overall Max TPS)
- `CurrentTransactionsPerSecond` from `KpiStats-*.csv` grouped by `PolicyServer` (Overall Current TPS)
- `MaxTPSPercentageOfCapacity` from `KpiStats-*.csv` grouped by `PolicyServer` (TPS vs capacity)
- `CurrentSessionCount` from `KpiStats-*.csv` grouped by `PolicyServer` (Active PCRF sessions)
- `CurrentSessionPercentageOfCapacity` from `KpiStats-*.csv` grouped by `PolicyServer` (Sessions vs capacity)
- `CurrentPDNConnectionCount` from `KpiStats-*.csv` grouped by `PolicyServer` (PDN connections)
- `CurrentPDNConnectionPercentageOfCapacity` from `KpiStats-*.csv` grouped by `PolicyServer` (PDN vs capacity)
- `LoadSheddingStatus` from `KpiStats-*.csv` grouped by `PolicyServer` (State timeline)
- `LoadSheddingEfficiency` from `KpiStats-*.csv` grouped by `PolicyServer`
- `LoadSheddingDistressCount` from `KpiStats-*.csv` grouped by `PolicyServer`
- `PrimaryCPUUtilizationPercentage` from `KpiStats-*.csv` grouped by `PolicyServer`
- `PrimaryMemoryUtilizationPercentage` from `KpiStats-*.csv` grouped by `PolicyServer`
- `PrimaryDiskUtilizationPercentage` from `KpiStats-*.csv` grouped by `PolicyServer`
- `CurrentProtocolErrorSentCount` from `KpiStats-*.csv` grouped by `PolicyServer`
- `CurrentProtocolErrorReceivedCount` from `KpiStats-*.csv` grouped by `PolicyServer`

### PFE/MRA Overview

- `PcefCCRICurrentTPS` from `TpsMraStats-*.csv` grouped by `MRA` (CCR-I)
- `PcefCCRIMaxTPS` from `TpsMraStats-*.csv` grouped by `MRA` (CCR-I)
- `PcefCCRUCurrentTPS` from `TpsMraStats-*.csv` grouped by `MRA` (CCR-U)
- `PcefCCRTCurrentTPS` from `TpsMraStats-*.csv` grouped by `MRA` (CCR-T)
- `PcefRARCurrentTPS` from `TpsMraStats-*.csv` grouped by `MRA` (RAR)
- `PcefGxSummaryCurrentTPS` from `TpsMraStats-*.csv` grouped by `MRA` (calculated as `PcefCCRICurrentTPS+PcefCCRUCurrentTPS+PcefCCRTCurrentTPS+PcefRARCurrentTPS`)
- `PcefGxSummaryMaxTPS` from `TpsMraStats-*.csv` grouped by `MRA` (calculated as `PcefCCRIMaxTPS+PcefCCRUCurrentTPS+PcefCCRTCurrentTPS+PcefRARCurrentTPS`)
- `AverageTransactionOutProcessingTime` from `DiameterMraPcefLatencyStats-*.csv` grouped by `MRA`
- `MaxTransactionOutProcessingTime` from `DiameterMraPcefLatencyStats-*.csv` grouped by `MRA`
- `CCRIMessagesTimeoutCount` from `DiameterMraPcefStats-*.csv` grouped by `MRA`
- `PeerDownCount` from `DiameterMraPcefStats-*.csv` grouped by `MRA`

### Sh Data Source

- `SuccessfulSearchCount` from `ShDataSourceStats-*.csv` grouped by `PolicyServer`
- `SearchErrorCount` from `ShDataSourceStats-*.csv` grouped by `PolicyServer`
- `AvgSuccessfulSearchTimeTaken` from `ShDataSourceStats-*.csv` grouped by `PolicyServer`
- `MaxSuccessfulSearchTimeTaken` from `ShDataSourceStats-*.csv` grouped by `PolicyServer`

### Sh Health

- `UDRMessagesTimeoutCount` from `DiameterShStats-*.csv` grouped by `PolicyServer`
- `SNRMessagesTimeoutCount` from `DiameterShStats-*.csv` grouped by `PolicyServer`
- `PeerDownCount` from `DiameterShStats-*.csv` grouped by `PolicyServer`
- `CurrentConnectionsCount` from `DiameterShStats-*.csv` grouped by `PolicyServer`

### Sh Latency

- `AverageTransactionOutProcessingTime` from `DiameterShLatencyStats-*.csv` grouped by `PolicyServer`
- `MaxTransactionOutProcessingTime` from `DiameterShLatencyStats-*.csv` grouped by `PolicyServer`
- `TransactionTime_Out_gt_200_Count` from `DiameterShLatencyStats-*.csv` grouped by `PolicyServer` (Tail (>200ms))

### Sh TPS

- `ShUDRSentTCurrentTPS` from `TpsStats-*.csv` grouped by `PolicyServer` (UDR)
- `ShPNRCurrentTPS` from `TpsStats-*.csv` grouped by `PolicyServer` (PNR)
- `ShPURCurrentTPS` from `TpsStats-*.csv` grouped by `PolicyServer` (PUR)
- `ShSNRCurrentTPS` from `TpsStats-*.csv` grouped by `PolicyServer` (SNR)

### Sy Data Source

- `SuccessfulSearchCount` from `SyDataSourceStats-*.csv` grouped by `PolicyServer`
- `UnsuccessfulSearchCount` from `SyDataSourceStats-*.csv` grouped by `PolicyServer`
- `AvgSuccessfulSearchTimeTaken` from `SyDataSourceStats-*.csv` grouped by `PolicyServer`
- `AvgUnsuccessfulSearchTimeTaken` from `SyDataSourceStats-*.csv` grouped by `PolicyServer`

### Sy Health

- `SLRMessagesTimeoutCount` from `DiameterSyStats-*.csv` grouped by `PolicyServer`
- `SLRIMessagesTimeoutCount` from `DiameterSyStats-*.csv` grouped by `PolicyServer`
- `STRMessagesTimeoutCount` from `DiameterSyStats-*.csv` grouped by `PolicyServer`
- `PeerDownCount` from `DiameterSyStats-*.csv` grouped by `PolicyServer`
- `CurrentConnectionsCount` from `DiameterSyStats-*.csv` grouped by `PolicyServer`

### Sy Latency

- `AverageTransactionOutProcessingTime` from `DiameterSyLatencyStats-*.csv` grouped by `PolicyServer`
- `MaxTransactionOutProcessingTime` from `DiameterSyLatencyStats-*.csv` grouped by `PolicyServer`
- `TransactionTime_Out_gt_200_Count` from `DiameterSyLatencyStats-*.csv` grouped by `PolicyServer` (Tail (>200ms))

### Sy TPS

- `SySLRICurrentTPS` from `TpsStats-*.csv` grouped by `PolicyServer` (SLR-I)
- `SySLRUCurrentTPS` from `TpsStats-*.csv` grouped by `PolicyServer` (SLR-U)
- `SySNRTCurrentTPS` from `TpsStats-*.csv` grouped by `PolicyServer` (SNR)
- `SySTRCurrentTPS` from `TpsStats-*.csv` grouped by `PolicyServer` (STR)

