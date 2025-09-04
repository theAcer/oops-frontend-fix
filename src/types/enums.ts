export enum BusinessType {
  RESTAURANT = "restaurant",
  SALON = "salon",
  RETAIL = "retail",
  SERVICE = "service",
  OTHER = "other",
}

export enum CampaignType {
  DISCOUNT = "discount",
  POINTS_BONUS = "points_bonus",
  FREE_ITEM = "free_item",
  CASHBACK = "cashback",
  REFERRAL = "referral",
}

export enum CampaignStatus {
  DRAFT = "draft",
  SCHEDULED = "scheduled",
  ACTIVE = "active",
  PAUSED = "paused",
  COMPLETED = "completed",
  CANCELLED = "cancelled",
}

export enum TargetAudience {
  ALL_CUSTOMERS = "all_customers",
  NEW_CUSTOMERS = "new_customers",
  REGULAR_CUSTOMERS = "regular_customers",
  VIP_CUSTOMERS = "vip_customers",
  AT_RISK_CUSTOMERS = "at_risk_customers",
  CHURNED_CUSTOMERS = "churned_customers",
  CUSTOM_SEGMENT = "custom_segment",
}

export enum LoyaltyProgramType {
  POINTS = "points",
  VISITS = "visits",
  SPEND = "spend",
  HYBRID = "hybrid",
}

export enum NotificationType {
  SMS = "sms",
  EMAIL = "email",
  WHATSAPP = "whatsapp",
  PUSH = "push",
  PROMOTIONAL = "promotional",
  LOYALTY = "loyalty",
  RETENTION = "retention",
}

export enum NotificationStatus {
  PENDING = "pending",
  SENT = "sent",
  DELIVERED = "delivered",
  FAILED = "failed",
  BOUNCED = "bounced",
}

export enum TransactionStatus {
  PENDING = "pending",
  COMPLETED = "completed",
  FAILED = "failed",
  REVERSED = "reversed",
}

export enum TransactionType {
  PAYMENT = "payment",
  REFUND = "refund",
  REVERSAL = "reversal",
}