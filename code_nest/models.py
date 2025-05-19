from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from datetime import date
from django.utils import timezone
from django.utils.text import slugify
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError

                                        # --------------------------
                                        # CustomUser MODEL
                                        # --------------------------
class CustomUser(AbstractUser):

    age = models.IntegerField(null=True, blank=True)
    email_confirm = models.BooleanField(default=False) # Default unconfirmed email
    ranking_position = models.IntegerField(default= 0)
    XP = models.IntegerField(default=0)
    code = models.CharField(max_length=100, unique=True, null=True, blank=True) # Unique code for confirmation

    
    groups = models.ManyToManyField(
        "auth.Group",
        related_name="customuser_set",
        blank=True
    )
    user_permissions = models.ManyToManyField(
        "auth.Permission",
        related_name="customuser_permissions_set",
        blank=True
    )
    
    @property
    def testattempts(self):
        return self.testattempt_set.all()

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
        max_length=50,
        choices=[("Beginner", "Beginner"), ("Intermediate", "Intermediate"), ("Advanced", "Advanced")],
        default="Beginner"
    )
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_free = models.BooleanField(default=False)
    image = models.ImageField(upload_to='course_images/', blank=True, null=True)
    slug = models.SlugField(blank=True, null=True)

    is_published = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

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
    categories = models.ManyToManyField(Category)
    title = models.CharField(max_length=255)
    description = models.TextField()
    difficulty = models.CharField(
        max_length=50, choices=[("Beginner", "Beginner"), ("Intermediate", "Intermediate"), ("Advanced", "Advanced")], 
        default="Beginner"
    )
    number_of_questions = models.IntegerField()
    image = models.ImageField(upload_to='tests/', default='tests/default.png')
    time = models.DurationField(default="00:30:00")
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def time_in_minutes(self):
        return int(self.time.total_seconds() // 60)
    

    @property
    def average_score(self):
        # Remove the completed=True filter to include all attempts
        avg = self.testresult_set.aggregate(
            avg_score=models.Avg('percentage')  # Use percentage instead of score
        )['avg_score']
        return round(avg, 1) if avg is not None else 0

    @property
    def completion_rate(self):
        total_attempts = self.testresult_set.count()
        if total_attempts == 0:
            return 0  # Avoid division by zero
        
        perfect_scores = self.testresult_set.filter(completed=True).count()
        completion_rate = (perfect_scores / total_attempts) * 100
        
        # Round to 1 decimal place for better precision
        return round(completion_rate, 1)

    @property
    def attempts_count(self):
        return self.testresult_set.count()
    

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
    
    class Meta:
        ordering = ['option_label']

                                        # --------------------------
                                        # TESTRESULT MODEL
                                        # --------------------------

class TestResult(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="testresults")
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    score = models.FloatField()
    completed = models.BooleanField(default=False)
    percentage = models.FloatField(default=0)
    date_taken = models.DateTimeField(auto_now_add=True)
    cooldown_until = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'test'],
                name='unique_user_test'
            )
        ]
    
    @property
    def is_active_cooldown(self):
        return False  # Întotdeauna False acum
    
                                       
   
                                        # --------------------------
                                        # USERANSWER MODEL
                                        # --------------------------
  
class UserAnswer(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    test_result = models.ForeignKey(TestResult, on_delete=models.CASCADE)
    selected_answer = models.ForeignKey(Answer, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'question', 'test_result')

    def __str__(self):
        return f"{self.user.username} - {self.question.text[:50]}"
    
    
    
                                        # --------------------------
                                        # FORUMQUESTION MODEL
                                        # --------------------------
                                        
class ForumQuestion(models.Model):
    title = models.CharField(max_length=255)
    body = models.TextField()
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    
    
                                        # --------------------------
                                        # FORUMANSWER MODEL
                                        # --------------------------    
                                        
                                        
class ForumAnswer(models.Model):
    question = models.ForeignKey(ForumQuestion, on_delete=models.CASCADE, related_name='forum_answers')
    body = models.TextField()
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Răspuns la: {self.question.title}"                                        