from django.contrib import admin
from .models import (
    CustomUser, Category, Course, CourseEnrollment, 
    Review, Test, Question, Answer,TestResult,UserAnswer,ForumAnswer,ForumQuestion
)


class TestResultInline(admin.TabularInline):  # Sau admin.StackedInline pentru un layout diferit
    model = TestResult
    extra = 0  # Nu afișa câmpuri goale în plus
    readonly_fields = ('test', 'score', 'date_taken')  # Opțional: face câmpurile readonly
    #can_delete = False  # Opțional: dezactivează ștergerea din inline

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'age', 'ranking_position', 'XP', 'email_confirm', 'is_staff', 'is_superuser')
    search_fields = ('username', 'email')
    list_filter = ('email_confirm', 'ranking_position', 'is_staff', 'is_superuser')
    inlines = [TestResultInline]


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'title')
    search_fields = ('title',)
    list_per_page = 20


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'difficulty', 'price', 'is_free')
    list_filter = ('difficulty', 'is_free', 'category')
    search_fields = ('title',)
    list_per_page = 20


@admin.register(CourseEnrollment)
class CourseEnrollmentAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'purchase_date', 'status', 'completion_date', 'payment_method')
    list_filter = ('status', 'payment_method')
    search_fields = ('user__username', 'course__title')


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'rating', 'posted_date')
    list_filter = ('rating',)
    search_fields = ('user__username', 'course__title')


@admin.register(Test)
class TestAdmin(admin.ModelAdmin):
    list_display = ('id','title', 'get_categories', 'difficulty', 'number_of_questions')
    list_filter = ('difficulty', 'categories')  
    search_fields = ('title',)

    def get_categories(self, obj):
        return ", ".join([cat.title for cat in obj.categories.all()])
    get_categories.short_description = 'Categories'



class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 1  # Numărul de răspunsuri implicite pentru fiecare întrebare


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'test', 'text', 'points')
    search_fields = ('text',)
    list_filter = ('test',)
    inlines = [AnswerInline]  # 


# @admin.register(Answer)
# class AnswerAdmin(admin.ModelAdmin):
#     list_display = ('question', 'option_label', 'text', 'is_correct')
#     list_filter = ('is_correct',)
#     search_fields = ('text', 'question__text')


@admin.register(UserAnswer)
class UserAnswerAdmin(admin.ModelAdmin):
    list_display=('user__username','question__id','question__test','selected_answer')


@admin.register(ForumQuestion)
class ForumQuestionAdmin(admin.ModelAdmin):
    list_display=('author__username','title','created_at')
    
    
@admin.register(ForumAnswer)
class ForumAnswerAdmin(admin.ModelAdmin):
    list_display=('author__username','question__title','created_at')