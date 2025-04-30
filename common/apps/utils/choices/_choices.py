
NOTIFICATION_TYPES = [
        ('interaction', 'Interaction'),
        ('comment', 'Comment'),
        ('system', 'System')
]


INTERACTION_TYPES = [
        ('like', 'Like'),
        ('dislike', 'Dislike'),
        ('favorite', 'Favorite')
]
    
ADDRESS_TYPES = [
        ('billing', 'Billing'),
        ('shipping', 'Shipping')
] 

ORDER_STATUS_CHOICES = (
        ('confirmed', 'Confirmed'),
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'), 
)

TRANSCRIPTION_STATUS = [
        ('processing', 'Processing'),
        ('completed', 'Completed')
]


VIEW_TYPES = [
        ('private', 'Private'),
        ('public', 'Public')
]

PAYMENT_STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
)

PAYMENT_METHOD_CHOICES = (
        ('stripe', 'Stripe'),
        ('paypal', 'PayPal'),
        ('manual', 'Manual'),
        ('cheque', 'Cheque'),
        ('bank_transfer', 'Bank Transfer'),
        ('crypto', 'Crypto'),
        ('other', 'Other'),
)