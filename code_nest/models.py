from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from datetime import date
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError

                                        # --------------------------
                                        # CustomUser MODEL
                                        # --------------------------
class CustomUser(AbstractUser):

    age = models.IntegerField(null=False, blank=False)
    email_confirm = models.BooleanField(default=False) # Default unconfirmed email
    ranking_position = models.IntegerField(default= 0)
    XP = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.username})"
    
                                        # --------------------------
                                        # Category MODEL
                                        # --------------------------
class Category(models.Model):
    title = models.CharField(max_length=255)
    descripition = models.TextField()

    def __str__(self):
        return self.title
    
                                        # --------------------------
                                        # MODEL Course
                                        # --------------------------
class Course(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="courses")
    title = models.CharField(max_length=255)
    description = models.TextField()
    difficulty = models.CharField(
        max_length=50, choices=[("Beginner", "Beginner"), ("Intermediate", "Intermediate"), ("Advanced", "Advanced")], 
        default="Beginner"
    )
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_free = models.BooleanField(default=False)

    def __str__(self):
        return self.title

                                        # --------------------------
                                        # COURSE ENROLLMENT (Many-to-Many Relationship)
                                        # --------------------------

class CourseEnrollment(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    purchase_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=50, choices=[("unstarted", "Unstarted"), ("in progress", "In progress"), ("finished", "Finished")], 
        default="Unstarted"
    )
    completion_date = models.DateTimeField(null=True, blank=True)
    payment_method = models.CharField(
        max_length=50, choices=[("card", "Credit Card"), ("paypal", "PayPal"), ("free", "Free")], default="free"
    )

    class Meta:
        unique_together = ("user", "course")  # A user cannot enroll in the same course twice

    def __str__(self):
        return f"{self.user.username} - {self.course.title}"

                                        # --------------------------
                                        # COURSE REVIEWS
                                        # --------------------------
class Review(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="reviews")
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    text = models.TextField()
    rating = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)])  # Rating from 1 to 5
    posted_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.course.title} ({self.rating})"  
    
                                        # --------------------------
                                        # TESTS MODEL
                                        # --------------------------
class Test(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    difficulty = models.CharField(
        max_length=50, choices=[("Beginner", "Beginner"), ("Intermediate", "Intermediate"), ("Advanced", "Advanced")], 
        default="Beginner"
    )
    number_of_questions = models.IntegerField()

    def __str__(self):
        return self.title

                                        # --------------------------
                                        # QUESTIONS MODEL
                                        # --------------------------
class Question(models.Model):
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name="questions")
    text = models.TextField()
    points = models.FloatField()

    def __str__(self):
        return self.text
    
                                        # --------------------------
                                        # ANSWERS MODEL
                                        # --------------------------
class Answer(models.Model):
    OPTION_CHOICES = [
        ("A", "A"), 
        ("B", "B"), 
        ("C", "C"), 
        ("D", "D"), 
        ("E", "E"), 
        ("F", "F")
    ]
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="answers")
    option_label = models.CharField(max_length=1, choices=OPTION_CHOICES)    
    text = models.TextField()
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.option_label}: {self.text}"
