
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

COLLECTION_TYPES = [
        ('personal', 'Personal'),
        ('shared', 'Shared'), 
        ('meta', 'Meta'), 
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


ORDER_STATUS_CHOICES = (
    (1, "Order Confirmed"),
    (2, "Order Confirmed"),
    (3, "Payment Pending"),
    (4, "Payment Confirmed"), 
    (5, "Order Packed/Ready to Pickup"),
    (6, "Processing"), 
    (7, "Cancelled due to Merchant Inactivity."),
    (8, "Shipped"),
    (9, "Out for Delivery"),
    (10, "Delivery Reached Destination"),
    (11, "Delivered"), 
    (12, "Return Initiated"),
    (13, "Return Received"),
    (14, "Refund Initiated"),
    (15, "Refund Completed"), 
    (16, "Service Completed"),
    (17, "Review Pending"),
    (18, "Service Reviewed"),
    (19, "Invoice Generated"),
    (20, "Invoice Paid"),
    (21, "Order Rejected"),
    (22, "Failed Delivery"),
)

SIZE_CHOICES = (
    ('S', 'Small'),
    ('M', 'Medium'),
    ('L', 'Large'),
    ('XL', 'Extra Large'),
    ('XXL', 'Extra Extra Large'),
)

CANVAS_RATIO = (
    ('9:16', '9:16'),
    ('16:9', '16:9'),
    ('1:1', '1:1'),
    ('4:3', '4:3'),
    ('5:4', '5:4'),
    ('3:2', '3:2'),
    ('2:3', '2:3'),
    ('2:1', '2:1'),
    ('1:2', '1:2'),
)

   
# Convert to dictionary for fast lookup
STATUS_DICT = dict(ORDER_STATUS_CHOICES)