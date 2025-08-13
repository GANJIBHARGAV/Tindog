namespace SlaBreach.Domain;

public enum Comparator { Gt, Gte, Lt, Lte }
public enum Severity { Low, Medium, High, Critical }
public enum SlaStatusState { Normal, AtRisk, Breached, Recovered }
public enum IncidentStatus { Open, Acknowledged, Resolved }
