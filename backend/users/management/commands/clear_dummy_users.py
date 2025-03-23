from django.core.management.base import BaseCommand
from users.models import CustomUser, Organization
from django.db.models import Q
import re

class Command(BaseCommand):
    help = 'Clears dummy donor and organization accounts from the database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Skip confirmation prompt',
        )
        parser.add_argument(
            '--donor',
            action='store_true',
            help='Delete only donor accounts',
        )
        parser.add_argument(
            '--organization',
            action='store_true',
            help='Delete only organization accounts',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        force = options['force']
        only_donors = options['donor']
        only_organizations = options['organization']
        
        # Define patterns for identifying dummy accounts
        dummy_patterns = [
            r'test',
            r'dummy',
            r'example',
            r'demo',
            r'fake',
            r'sample',
        ]
        
        # Build query for dummy accounts
        dummy_q = Q()
        for pattern in dummy_patterns:
            dummy_q |= (
                Q(username__icontains=pattern) | 
                Q(email__icontains=pattern) | 
                Q(first_name__icontains=pattern) | 
                Q(last_name__icontains=pattern)
            )
        
        # Filter by user type if specified
        user_filter = Q()
        if only_donors and not only_organizations:
            user_filter = Q(user_type='DONOR')
            self.stdout.write('Filtering for donor accounts only')
        elif only_organizations and not only_donors:
            user_filter = Q(user_type='ORGANIZATION')
            self.stdout.write('Filtering for organization accounts only')
        
        # Get the dummy users
        dummy_users = CustomUser.objects.filter(dummy_q & user_filter & ~Q(user_type='ADMIN'))
        
        # Count before deletion
        donor_count = dummy_users.filter(user_type='DONOR').count()
        org_count = dummy_users.filter(user_type='ORGANIZATION').count()
        total_count = dummy_users.count()
        
        if dry_run:
            self.stdout.write(f"DRY RUN: Would delete {total_count} users:")
            self.stdout.write(f" - {donor_count} dummy donors")
            self.stdout.write(f" - {org_count} dummy organizations")
            
            # Show a sample of users that would be deleted
            if total_count > 0:
                self.stdout.write("\nSample users that would be deleted:")
                for user in dummy_users[:10]:  # Show at most 10 users
                    self.stdout.write(f" - {user.username} ({user.email}) - {user.user_type}")
                if total_count > 10:
                    self.stdout.write(f"...and {total_count - 10} more")
            return
        
        # Ask for confirmation unless --force is used
        if not force:
            self.stdout.write(f"About to delete {total_count} users:")
            self.stdout.write(f" - {donor_count} dummy donors")
            self.stdout.write(f" - {org_count} dummy organizations")
            
            confirmation = input("Are you sure you want to proceed? [y/N] ")
            if confirmation.lower() != 'y':
                self.stdout.write("Operation cancelled.")
                return
        
        # Delete the dummy users
        dummy_users.delete()
        
        self.stdout.write(self.style.SUCCESS(f"Successfully deleted {total_count} dummy users:"))
        self.stdout.write(f" - {donor_count} dummy donors")
        self.stdout.write(f" - {org_count} dummy organizations") 