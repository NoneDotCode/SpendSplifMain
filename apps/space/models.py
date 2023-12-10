from django.db import models

from apps.customuser.models import CustomUser


class Space(models.Model):
    """
    Model representing a space.
    """

    title = models.CharField(max_length=24)
    members = models.ManyToManyField(CustomUser, verbose_name="members", through="MemberPermissions")

    def __str__(self):
        return self.title


class MemberPermissions(models.Model):
    member = models.ForeignKey(CustomUser, verbose_name="member", on_delete=models.CASCADE)
    space = models.ForeignKey(Space, verbose_name="space", on_delete=models.CASCADE)
    owner = models.BooleanField(default=False)
    """Users"""
    remove_users = models.BooleanField(default=True, verbose_name="can remove users from space")
    edit_users = models.BooleanField(default=True, verbose_name="can edit users' permissions in space")
    add_users = models.BooleanField(default=True, verbose_name="can add users to space")
    """Accounts"""
    delete_accounts = models.BooleanField(default=True, verbose_name="can delete accounts")
    edit_accounts = models.BooleanField(default=True, verbose_name="can edit accounts")
    create_accounts = models.BooleanField(default=True, verbose_name="can create accounts")
    """Categories"""
    delete_categories = models.BooleanField(default=True, verbose_name="can delete categories")
    edit_categories = models.BooleanField(default=True, verbose_name="can edit categories")
    create_categories = models.BooleanField(default=True, verbose_name="can create categories")
    """History"""
    edit_history = models.BooleanField(default=True, verbose_name="can edit history records")
    delete_history = models.BooleanField(default=True, verbose_name="can delete history records")
    """Goals"""
    delete_goals = models.BooleanField(default=True, verbose_name="can delete goals")
    edit_goals = models.BooleanField(default=True, verbose_name="can edit goals")
    create_goals = models.BooleanField(default=True, verbose_name="can create goals")
    """Recurring spends"""
    create_recurring_spends = models.BooleanField(default=True, verbose_name="can create recurring spends")
    edit_recurring_spends = models.BooleanField(default=True, verbose_name="can edit recurring spends")
    delete_recurring_spends = models.BooleanField(default=True, verbose_name="can delete recurring spends")
    """Bank Accounts"""
    add_bank_accounts = models.BooleanField(default=True, verbose_name="can add bank accounts to space")
    remove_bank_accounts = models.BooleanField(default=True, verbose_name="can remove bank accounts from space")
    """Basic perms"""
    spend = models.BooleanField(default=True, verbose_name="can spends")
    transfer = models.BooleanField(default=True, verbose_name="can transfers")
