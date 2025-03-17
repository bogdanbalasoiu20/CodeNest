from django.db import models

class TestTable(models.Model):
    field1=models.CharField(max_length=255)
    field2=models.IntegerField()
    field3=models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return self.field1
