from django.db import models
import uuid
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail


class User(AbstractUser):
    manager=models.BooleanField(default=False,null=True)
    worker=models.BooleanField(default=False,null=True)
    email=models.EmailField(unique=True,null=True)
    REQUIRED_FIELDS = []
    
    def __str__(self):
        return self.username
class Courier(models.Model):
         name=models.CharField(max_length=20)
         customer= models.ForeignKey(User,on_delete=models.CASCADE)
         destination=models.TextField()
         id=models.UUIDField(primary_key=True,default=uuid.uuid4,unique=True,editable=False)
         courier_id=models.CharField(max_length=50,default=uuid.uuid4)
         created=models.DateTimeField(auto_now=True)
         status=models.CharField(max_length=10,default="In Transit")
         delivery_by=models.CharField(max_length=20,default=None,null=True,blank=True)
         def __str__(self):
             return self.name[:20]

class ContactMessage(models.Model):
    name1 = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()

    def __str__(self):
        return self.name1
class Courierform(models.Model):
    namee = models.CharField(max_length=255, blank=True, null=True)
    contactPhone = models.CharField(max_length=20)
    pickupAddress = models.TextField()
    sender_email = models.EmailField()
    receiver_email = models.EmailField()
    emergencyContactName = models.CharField(max_length=255, blank=True, null=True)
    emergencyContactPhone = models.CharField(max_length=20, blank=True, null=True)
    deliveryAddress = models.TextField(blank=True, null=True)
    pickupTime = models.CharField(max_length=100, blank=True, null=True)
    ampm = models.CharField(
    max_length=2,
    choices=[('am', 'AM'), ('pm', 'PM')],
    default='am'
)
    packageSize = models.CharField(
        max_length=10,
        choices=[('small', 'Small'), ('medium', 'Medium'), ('large', 'Large')],
        default='small'
    )
    packageCategory = models.CharField(max_length=255, blank=True, null=True)
    packageWeight = models.FloatField()
    serviceType = models.CharField(
        max_length=20,
        choices=[('standard', 'Standard'), ('express', 'Express')],
        default='standard'
    )
    privacyPolicyAgreement = models.BooleanField()
    termsAgreement = models.BooleanField()

    def __str__(self):
        return self.namee
    
class Report(models.Model):
    report= models.TextField(null=True)
    created=models.DateTimeField(auto_now=True)
    courier=models.ForeignKey(Courier, on_delete=models.CASCADE,null=True)
    customer= models.ForeignKey(User, on_delete=models.CASCADE,null=True)
    id=models.UUIDField(primary_key=True,default=uuid.uuid4,unique=True,editable=False)
    report_id=models.CharField(max_length=50,default=uuid.uuid4)
    def __str__(self):
        return self.customer.username[:20]


class Branch(models.Model):
    name=models.CharField(max_length=20)
    manager=models.ForeignKey(User, on_delete=models.CASCADE)
    address=models.TextField()
    id=models.UUIDField(primary_key=True,default=uuid.uuid4,unique=True,editable=False)
    branch_id=models.CharField(max_length=50,default=uuid.uuid4)
    couriers=models.ManyToManyField(Courier,related_name="couriers",blank=True)
    delivery=models.ManyToManyField(User,related_name="deliverys",blank=True)
    reports=models.ManyToManyField(Report,related_name="reports",blank=True)
    
    def __str__(self):
        return self.name[:20]


class Tracker(models.Model):
    courier=models.ForeignKey(Courier, on_delete=models.CASCADE,null=True)
    customer= models.ForeignKey(User, on_delete=models.CASCADE,null=True)
    present= models.ForeignKey(Branch, on_delete=models.CASCADE,null=True)
    def __str__(self):
        return self.courier.name[:20]


@receiver(post_save,sender=Courier)
def create_tracker(sender,instance,created,**kwargs):
    if created:
        Tracker.objects.create(courier=instance,customer=instance.customer)



def send_email_on_courier_creation(instance, created):
    if created:
        subject = 'New Courier Created'
        message = f'A new courier with name: {instance.name}, ID: {instance.courier_id}, and destination: {instance.destination} has been created.'
        from_email = 'courierconnect11@gmail.com'
        recipient_list = [instance.customer.email]
        send_mail(subject, message, from_email, recipient_list)

@receiver(post_save, sender=Courier)
def send_email_on_courier_creation_handler(sender, instance, created, **kwargs):
    send_email_on_courier_creation(instance, created)









