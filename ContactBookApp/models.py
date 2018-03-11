from django.db import models

"""
Contact Model
-----------------
Name of the contact, Email Associated and owner who created the contact
"""
class Contact(models.Model):
	name = models.CharField(max_length=100)
	email = models.EmailField(max_length=100, unique=True)
	owner = models.ForeignKey('auth.User',
	                        related_name='contact',
	                        on_delete=models.CASCADE)

	def __str__(self):
		return self.email