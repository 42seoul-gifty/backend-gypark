from django.db import models
from django.db.models import Q


class ActivedQuerysetManager(models.Manager):
     def actived(self):
        return self.get_queryset().filter(is_active=True)


class ProductManager(models.Manager):
    def actived(self):
        '''
        age 중에 is_active가 있고,
        gender 중에 is_active가 있고,
        price가 is_active인 것
        '''
        return self.get_queryset().filter(
            Q(age__is_active=True) &
            Q(gender__is_active=True) &
            Q(price__is_active=True)
        ).distinct()

