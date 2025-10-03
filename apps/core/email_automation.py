"""
Email Marketing Automation System
"""
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class EmailCampaignManager:
    """
    Manages email campaigns and automation.
    """
    
    @staticmethod
    def send_welcome_email(user):
        """Send welcome email to new user."""
        subject = f"Welcome to {settings.SITE_NAME}!"
        
        context = {
            'user': user,
            'site_name': settings.SITE_NAME,
            'site_url': settings.SITE_URL,
        }
        
        html_content = render_to_string('emails/welcome.html', context)
        text_content = render_to_string('emails/welcome.txt', context)
        
        return EmailCampaignManager._send_email(
            subject=subject,
            to_email=user.email,
            html_content=html_content,
            text_content=text_content
        )
    
    @staticmethod
    def send_subscription_confirmation(subscription):
        """Send subscription confirmation email."""
        subject = f"Subscription Confirmed - {subscription.tier.name}"
        
        context = {
            'subscription': subscription,
            'user': subscription.user,
            'tier': subscription.tier,
            'site_name': settings.SITE_NAME,
            'billing_portal_url': f"{settings.SITE_URL}/monetization/billing/",
        }
        
        html_content = render_to_string('emails/subscription_confirmed.html', context)
        text_content = render_to_string('emails/subscription_confirmed.txt', context)
        
        return EmailCampaignManager._send_email(
            subject=subject,
            to_email=subscription.user.email,
            html_content=html_content,
            text_content=text_content
        )
    
    @staticmethod
    def send_payment_failed_email(subscription):
        """Send payment failed notification."""
        subject = "Payment Failed - Action Required"
        
        context = {
            'subscription': subscription,
            'user': subscription.user,
            'tier': subscription.tier,
            'site_name': settings.SITE_NAME,
            'billing_portal_url': f"{settings.SITE_URL}/monetization/billing/",
        }
        
        html_content = render_to_string('emails/payment_failed.html', context)
        text_content = render_to_string('emails/payment_failed.txt', context)
        
        return EmailCampaignManager._send_email(
            subject=subject,
            to_email=subscription.user.email,
            html_content=html_content,
            text_content=text_content
        )
    
    @staticmethod
    def send_affiliate_commission_email(commission):
        """Send commission notification to affiliate."""
        subject = f"New Commission Earned: ${commission.commission_amount}"
        
        context = {
            'commission': commission,
            'program': commission.program,
            'tool': commission.link.tool,
            'site_name': settings.SITE_NAME,
        }
        
        # Would need user/affiliate relationship for this
        # Placeholder for now
        logger.info(f"Commission email queued: {commission.id}")
        return True
    
    @staticmethod
    def send_weekly_digest(user, content_data: Dict[str, Any]):
        """Send weekly content digest to user."""
        subject = f"Your Weekly Digest from {settings.SITE_NAME}"
        
        context = {
            'user': user,
            'site_name': settings.SITE_NAME,
            'new_tools': content_data.get('new_tools', []),
            'trending_tools': content_data.get('trending_tools', []),
            'new_comparisons': content_data.get('new_comparisons', []),
            'week_start': content_data.get('week_start'),
            'week_end': content_data.get('week_end'),
        }
        
        html_content = render_to_string('emails/weekly_digest.html', context)
        text_content = render_to_string('emails/weekly_digest.txt', context)
        
        return EmailCampaignManager._send_email(
            subject=subject,
            to_email=user.email,
            html_content=html_content,
            text_content=text_content
        )
    
    @staticmethod
    def send_tool_update_notification(user, tool, update_info: str):
        """Send notification about tool update."""
        subject = f"Update: {tool.name}"
        
        context = {
            'user': user,
            'tool': tool,
            'update_info': update_info,
            'tool_url': f"{settings.SITE_URL}{tool.get_absolute_url()}",
            'site_name': settings.SITE_NAME,
        }
        
        html_content = render_to_string('emails/tool_update.html', context)
        text_content = render_to_string('emails/tool_update.txt', context)
        
        return EmailCampaignManager._send_email(
            subject=subject,
            to_email=user.email,
            html_content=html_content,
            text_content=text_content
        )
    
    @staticmethod
    def send_comparison_ready_email(user, comparison):
        """Send notification that AI comparison is ready."""
        subject = "Your Comparison is Ready!"
        
        context = {
            'user': user,
            'comparison': comparison,
            'comparison_url': f"{settings.SITE_URL}{comparison.get_absolute_url()}",
            'site_name': settings.SITE_NAME,
        }
        
        html_content = render_to_string('emails/comparison_ready.html', context)
        text_content = render_to_string('emails/comparison_ready.txt', context)
        
        return EmailCampaignManager._send_email(
            subject=subject,
            to_email=user.email,
            html_content=html_content,
            text_content=text_content
        )
    
    @staticmethod
    def _send_email(subject: str, to_email: str, html_content: str, text_content: str, from_email: str = None) -> bool:
        """
        Internal method to send email.
        
        Returns:
            True if successful, False otherwise
        """
        if not from_email:
            from_email = settings.DEFAULT_FROM_EMAIL
        
        try:
            msg = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=from_email,
                to=[to_email]
            )
            msg.attach_alternative(html_content, "text/html")
            msg.send()
            
            logger.info(f"Email sent successfully to {to_email}: {subject}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending email to {to_email}: {str(e)}")
            return False


class NewsletterManager:
    """
    Manages newsletter subscriptions and campaigns.
    """
    
    @staticmethod
    def subscribe_user(email: str, preferences: Dict[str, bool] = None):
        """Subscribe user to newsletter."""
        from apps.core.models import NewsletterSubscriber
        
        subscriber, created = NewsletterSubscriber.objects.get_or_create(
            email=email,
            defaults={
                'is_active': True,
                'preferences': preferences or {
                    'weekly_digest': True,
                    'new_tools': True,
                    'comparisons': True,
                    'promotions': False,
                }
            }
        )
        
        if not created:
            subscriber.is_active = True
            if preferences:
                subscriber.preferences = preferences
            subscriber.save()
        
        # Send welcome email
        if created:
            NewsletterManager._send_newsletter_welcome(subscriber)
        
        return subscriber
    
    @staticmethod
    def unsubscribe_user(email: str, token: str = None):
        """Unsubscribe user from newsletter."""
        from apps.core.models import NewsletterSubscriber
        
        try:
            subscriber = NewsletterSubscriber.objects.get(email=email)
            subscriber.is_active = False
            subscriber.unsubscribed_at = timezone.now()
            subscriber.save()
            
            logger.info(f"User unsubscribed: {email}")
            return True
            
        except NewsletterSubscriber.DoesNotExist:
            logger.warning(f"Unsubscribe attempt for non-existent subscriber: {email}")
            return False
    
    @staticmethod
    def send_newsletter_campaign(subject: str, content: str, segment: str = 'all'):
        """
        Send newsletter to subscribers.
        
        Args:
            subject: Email subject
            content: HTML content
            segment: 'all', 'premium', 'free', or custom filter
        """
        from apps.core.models import NewsletterSubscriber
        
        # Get subscribers based on segment
        subscribers = NewsletterSubscriber.objects.filter(is_active=True)
        
        if segment == 'premium':
            from apps.monetization.models import PremiumSubscription
            premium_users = PremiumSubscription.objects.filter(
                status='active'
            ).values_list('user__email', flat=True)
            subscribers = subscribers.filter(email__in=premium_users)
        
        # Send in batches
        batch_size = 100
        sent_count = 0
        
        for i in range(0, subscribers.count(), batch_size):
            batch = subscribers[i:i + batch_size]
            
            for subscriber in batch:
                try:
                    EmailCampaignManager._send_email(
                        subject=subject,
                        to_email=subscriber.email,
                        html_content=content,
                        text_content=content  # Simplified for now
                    )
                    sent_count += 1
                except Exception as e:
                    logger.error(f"Error sending newsletter to {subscriber.email}: {str(e)}")
        
        logger.info(f"Newsletter campaign sent to {sent_count} subscribers")
        return sent_count
    
    @staticmethod
    def _send_newsletter_welcome(subscriber):
        """Send welcome email to new newsletter subscriber."""
        subject = f"Welcome to {settings.SITE_NAME} Newsletter!"
        
        context = {
            'subscriber': subscriber,
            'site_name': settings.SITE_NAME,
            'site_url': settings.SITE_URL,
            'unsubscribe_url': f"{settings.SITE_URL}/newsletter/unsubscribe/{subscriber.email}/",
        }
        
        html_content = render_to_string('emails/newsletter_welcome.html', context)
        text_content = render_to_string('emails/newsletter_welcome.txt', context)
        
        EmailCampaignManager._send_email(
            subject=subject,
            to_email=subscriber.email,
            html_content=html_content,
            text_content=text_content
        )


class AutomatedEmailTasks:
    """
    Celery tasks for automated email sending.
    """
    
    @staticmethod
    def send_weekly_digests():
        """Send weekly digests to all active users."""
        from django.contrib.auth import get_user_model
        from apps.tools.models import Tool, ToolComparison
        from datetime import timedelta
        
        User = get_user_model()
        week_ago = timezone.now() - timedelta(days=7)
        
        # Get content for digest
        new_tools = Tool.objects.filter(
            created_at__gte=week_ago,
            is_published=True
        )[:5]
        
        trending_tools = Tool.objects.filter(
            is_published=True,
            is_trending=True
        )[:5]
        
        new_comparisons = ToolComparison.objects.filter(
            created_at__gte=week_ago,
            is_published=True
        )[:3]
        
        content_data = {
            'new_tools': new_tools,
            'trending_tools': trending_tools,
            'new_comparisons': new_comparisons,
            'week_start': week_ago,
            'week_end': timezone.now(),
        }
        
        # Send to users who want weekly digests
        users = User.objects.filter(
            is_active=True,
            email__isnull=False
        )
        
        sent_count = 0
        for user in users:
            # Check user preferences (would need UserPreferences model)
            try:
                EmailCampaignManager.send_weekly_digest(user, content_data)
                sent_count += 1
            except Exception as e:
                logger.error(f"Error sending digest to {user.email}: {str(e)}")
        
        logger.info(f"Weekly digests sent to {sent_count} users")
        return sent_count
    
    @staticmethod
    def send_abandoned_comparison_reminders():
        """Send reminders for incomplete comparisons."""
        from apps.tools.models import ComparisonRequest
        from datetime import timedelta
        
        # Get comparison requests from 1-3 days ago that are still pending
        start_date = timezone.now() - timedelta(days=3)
        end_date = timezone.now() - timedelta(days=1)
        
        pending_requests = ComparisonRequest.objects.filter(
            status='pending',
            created_at__gte=start_date,
            created_at__lte=end_date,
            user__isnull=False
        )
        
        sent_count = 0
        for request in pending_requests:
            try:
                subject = "Your comparison is waiting!"
                context = {
                    'user': request.user,
                    'request': request,
                    'site_name': settings.SITE_NAME,
                }
                
                html_content = render_to_string('emails/comparison_reminder.html', context)
                text_content = render_to_string('emails/comparison_reminder.txt', context)
                
                EmailCampaignManager._send_email(
                    subject=subject,
                    to_email=request.user.email,
                    html_content=html_content,
                    text_content=text_content
                )
                sent_count += 1
                
            except Exception as e:
                logger.error(f"Error sending reminder: {str(e)}")
        
        logger.info(f"Sent {sent_count} comparison reminders")
        return sent_count
