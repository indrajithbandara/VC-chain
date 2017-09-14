from django.contrib.auth.models import User as AuthUser
        "img": user.avatar,
            "img": f.follower.avatar,
            "img": f.followed.email.avatar,
            "author_img": c.project.author.avatar,
        "author_img": project.author.avatar,


def editProfile(old_username, username, name, email, avatar, password):

    user = User.objects.filter(username__iexact=old_username).first()
    authuser = AuthUser.objects.filter(username__iexact=old_username).first()

    if user is None or authuser is None:
        raise Http404("User does not exist")

    if username:
        user.username = username
    if name:
        user.name = name
    if email:
        user.email = email
    if avatar:
        user.avatar = avatar

    if password:
        authuser.set_password(password)
    if username:
        authuser.username = username

    user.save()
    authuser.save()