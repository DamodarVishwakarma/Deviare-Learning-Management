import re
from lxml import html
from django.apps import apps
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from django.core.mail import (EmailMultiAlternatives, make_msgid)
from django.template import Template, Context
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


def read_uri(url):
    import mimetypes
    from urllib.parse import urlparse
    from os.path import exists
    import requests
    mime, n = mimetypes.guess_type(url)
    p = urlparse(url)
    if p.netloc == '':
        if exists(url):
            with open(url, 'rb') as f:
                data = f.read()
    else:
        r = requests.get(url)
        if r.ok:
            data = r.content
    return mime, data, p.path


def get_wrapped_email(
        email_data,
        email_tmpl="welcome_email",
        subject="Message from Deviare",
        recipients=None
        ):
    if recipients is None or email_data is None:
            return
    msg_html = render_to_string(email_tmpl, email_data, False)
    msg_html.update(prep_email_html(render_to_string("email_wrapper", dict(message_body=msg_html["body_html"]))))
    msg_html.update(
        dict(
            subject=subject,
            recipients=recipients,
        )
    )
    return msg_html


def send_wrapped_email(
        email_data,
        email_tmpl="welcome_email",
        subject="Message from Deviare",
        recipients=None
        ):
    if recipients is None or email_data is None:
            return
    msg_html = get_wrapped_email(
        email_data,
        email_tmpl=email_tmpl,
        subject=subject,
        recipients=recipients
        )

    return email_message(**msg_html)


def prep_email_html(source_code, BASE_NAME="image_"):
    import base64
    tree = html.fromstring(source_code)
    related = []
    for url in tree.xpath('//img[contains(@src, "/")]/@src'):
        if url.find('data:image') == -1:
            mime, img_data, rn = read_uri(url)
            base_type, image_type = mime.split('/', 1)
            pth = rn.replace('/', '').replace('.', '_').replace('@', '_')
            mime_image, cid = embed_image(img_data, pth, image_type)
            related.append(mime_image)
            source_code = source_code.replace(url, cid)

    for i, image in enumerate(tree.xpath('//img[contains(@src, "data:image")]/@src')):
        image_type, image_content = image.split(',', 1)
        image_type = re.findall('data:image\/(\w+);base64', image_type)[0]
        pth = "{}{}_{}".format(BASE_NAME, i, image_type)
        img_data = base64.b64decode(image_content)
        mime_image, cid = embed_image(img_data, pth, image_type)
        related.append(mime_image)
        source_code = source_code.replace(image, cid)

    return dict(body_html=source_code, related=related)


def make_cid(pth):
    cid = make_msgid(f'{pth}', domain='deviare.co.za')
    return cid[1:-1]


def embed_image(img_data, pth, image_type):
    cid = make_cid(pth)
    mime_image = MIMEImage(img_data, image_type)
    mime_image.add_header('Content-ID', f'<{cid}>')
    return mime_image, cid


def embed_text(text_data, pth, mime_type='calendar'):
    cid = make_cid(pth)
    mime_text = MIMEText(text_data, mime_type)
    mime_text.add_header('Content-ID', f'<{cid}>')
    return mime_text, cid


def render_to_string(template_name, context_src, html_only=True):

    EmailTemplate = apps.get_model('notification', 'EmailTemplate')
    base = EmailTemplate.get(template_name, html_only)
    context = Context(context_src)
    if html_only:
        tmpl = Template(base)
        return tmpl.render(context)
    ret = {}
    for key, text in base.items():
        tmpl = Template(text)
        ret[key] = tmpl.render(context)
    return ret


def ren_string_tmpl(tmpl_src='', context_src={}):
    context = Context(context_src)
    tmpl = Template(tmpl_src)
    return tmpl.render(context)


def cal_prep(cal, fn="invite"):
    part = MIMEText(cal.to_ical().decode("utf-8"), "calendar")
    part.add_header("Filename", f"{fn}.ics")
    part.add_header("Content-Disposition", f"attachment; filename={fn}.ics")
    return part


def email_message(subject="", body_text="", recipients=None, body_html="", related=None, attachments=None, **kwargs):
    if attachments is None:
        attachments = []
    if related is None:
        related = {}
    if recipients is None:
        recipients = []

    message = EmailMultiAlternatives(
        subject=subject,
        body=body_text,
        from_email="noreply@deviare.co.za",
        to=recipients,
        attachments=attachments,
        **kwargs,
    )
    if type(related) in (list, tuple):
        for r in related:
            message.attach(r)
    elif type(related) == dict():
        for pth, cid in related.items():
            message.attach(embed_image(pth, cid))
    # print(recipients)
    message.mixed_subtype = "related"
    message.attach_alternative(body_html, "text/html")
    return message.send(fail_silently=False)

