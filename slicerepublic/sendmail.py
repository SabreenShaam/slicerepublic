from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.template import Context
from django.utils.html import strip_tags


def send_booking_confirmation_mail_member(booking, to_email):
    _send_mail(
        subject='Booking confirmed for {} on {}'.format(booking.slice_class.name, booking.slice_class.start_date),
        sender=settings.EMAIL_SLICE_REPUBLIC_FROM,
        receiver=to_email,
        template_name='booking_confirmation_member',
        context={'booking': booking, 'user': booking.mbo_client.user},
    )


def send_booking_cancellation_mail_member(booking, cancelled_by, cancelled_date, to_email):
    _send_mail(
        subject='Cancellation of booking for {} on {}'.format(booking.slice_class.name, booking.slice_class.start_date),
        sender=settings.EMAIL_SLICE_REPUBLIC_FROM,
        receiver=to_email,
        template_name='booking_cancellation_member',
        context={'booking': booking, 'cancelled_by': cancelled_by, 'cancelled_date': cancelled_date, 'user': booking.mbo_client.user}
    )


def send_studio_staff_signup_verification_mail(staff_email, verification_code, to):
    _send_mail(
        subject="Staff Verification",
        sender=settings.EMAIL_SLICE_REPUBLIC_FROM,
        receiver=to,
        template_name='studio_staff_signup_verification',
        context={'staff_email': staff_email, 'verification_code': verification_code},
    )


def send_class_cancellation_emails(booking, class_info, cancelled_date):
    _send_mail(
        subject='Cancellation of class for {} on {}'.format(class_info.name, cancelled_date),
        sender=settings.EMAIL_SLICE_REPUBLIC_FROM,
        receiver=booking.mbo_client.user.email,
        template_name='class_cancellation_email',
        context={'booking': booking, 'class_info': class_info, 'cancelled_date': cancelled_date}
    )


def _send_mail(**kwargs):
    subject, from_email, to = kwargs.get('subject'), kwargs.get('sender'), kwargs.get('receiver')
    html = get_template('emails/%s.html' % kwargs.get('template_name'))
    context = kwargs.get('context')
    email_context = Context(context)
    html_content = html.render(email_context)
    text_content = strip_tags(html_content)

    if not isinstance(to, list):
        to = [to]

    msg = EmailMultiAlternatives(subject, text_content, from_email, to)
    msg.attach_alternative(html_content, 'text/html')
    attachments = kwargs.get('attachments')
    if attachments:
        for attachment in attachments:
            msg.attach(attachment.file_name, attachment.content, attachment.mime_type)
    msg.send()


def send_studio_user_signup_verification_mail(host_name, user_email, verification_code, to):
    _send_mail(
        subject="User Verification",
        sender=settings.EMAIL_SLICE_REPUBLIC_FROM,
        receiver=to,
        template_name='studio_user_signup_verification',
        context={'host_name': host_name, 'user_email': user_email, 'verification_code': verification_code},
    )


def send_signup_notification_email_to_studio(host_name, user_email, to):
    _send_mail(
        subject="User signup notification",
        sender=settings.EMAIL_SLICE_REPUBLIC_FROM,
        receiver=to,
        template_name='signup_notification_email_to_studio',
        context={'host_name': host_name, 'user_email': user_email},
    )


def send_auto_pay_update_notify_email(name, to):
    _send_mail(
        subject="Service Option Updated",
        sender=settings.EMAIL_SLICE_REPUBLIC_FROM,
        receiver=to,
        template_name='auto_pay_update_notification_email',
        context={'service_name': name},
    )


def send_api_integration_removal_notification(studio_name, to):
    _send_mail(
        subject="{} removed the API integration".format(studio_name),
        sender=settings.EMAIL_SLICE_REPUBLIC_FROM,
        receiver=to,
        template_name='api_integration_removal_notification',
        context={'studio_name': studio_name},
    )
