from vc_chain.models import User, Project, Star, Follow, Fork, Commit, File
from django.db.models import Q
import datetime
import difflib
    following_count = Follow.objects.filter(follower=user).count()
        "following": following_count,
        f_user = "" if p.forked_from is None else p.forked_from.author.username
        f_project = "" if p.forked_from is None else p.forked_from.name
            "forked_user": f_user,
            "forked_project": f_project,
    return [dict(t) for t in set([tuple(d.items()) for d in p_list])]
        f_user = "" if p.forked_from is None else p.forked_from.author.username
        f_project = "" if p.forked_from is None else p.forked_from.name
            "forked_user": f_user,
            "forked_project": f_project,
    return [dict(t) for t in set([tuple(d.items()) for d in p_list])]


def getFollowerData(username):
    user = User.objects.filter(username__iexact=username).first()

    if user is None:
        raise Http404("User does not exist")

    followers = Follow.objects.filter(followed=user)

    f_list = list()
    for f in followers:
        f_list.append({
            "name": f.follower.name,
            "username": f.follower.username,
            "email": f.follower.email,
            "img": "images/users/ccd-avatar.jpg",
        })

    return f_list


def getFollowingData(username):
    user = User.objects.filter(username__iexact=username).first()

    if user is None:
        raise Http404("User does not exist")

    following = Follow.objects.filter(follower=user)

    f_list = list()
    for f in following:
        f_list.append({
            "name": f.followed.name,
            "username": f.followed.username,
            "email": f.followed.email,
            "img": "images/users/ccd-avatar.jpg",
        })

    return f_list


def getTimelineData(username):
    user = User.objects.filter(username__iexact=username).first()

    if user is None:
        raise Http404("User does not exist")

    timeline_data = []

    stars_by_me = Star.objects.filter(user=user)
    for s in stars_by_me:
        timeline_data.append({
            "type": "star",
            "time": s.time,
            "puser": s.user.username,
            "suser": s.project.author.username,
            "sproject": s.project.name,
        })
    stars_to_me = Star.objects.filter(project__author=user)
    for s in stars_to_me:
        timeline_data.append({
            "type": "star",
            "time": s.time,
            "puser": s.user.username,
            "suser": s.project.author.username,
            "sproject": s.project.name,
        })
    forks_by_me = Fork.objects.filter(forked_project__author=user)
    for f in forks_by_me:
        timeline_data.append({
            "type": "fork",
            "time": f.time,
            "puser": f.forked_project.author.username,
            "suser": f.original_project.author.username,
            "pproject": f.forked_project.name,
            "sproject": f.original_project.name,
        })

    forks_to_me = Fork.objects.filter(original_project__author=user)
    for f in forks_to_me:
        timeline_data.append({
            "type": "fork",
            "time": f.time,
            "puser": f.forked_project.author.username,
            "suser": f.original_project.author.username,
            "pproject": f.forked_project.name,
            "sproject": f.original_project.name,
        })
    follow_me = Follow.objects.filter(followed=user)
    for f in follow_me:
        timeline_data.append({
            "type": "follow",
            "time": f.time,
            "puser": f.follower.username,
            "suser": f.followed.username,
        })
    follow_to = Follow.objects.filter(follower=user)
    for f in follow_to:
        timeline_data.append({
            "type": "follow",
            "time": f.time,
            "puser": f.follower.username,
            "suser": f.followed.username,
        })
    commits = Commit.objects.filter(project__author=user)
    for c in commits:
        timeline_data.append({
            "type": "commit",
            "time": c.time,
            "puser": c.project.author.username,
            "pproject": c.project.name,
            "branch": c.project.branch,
        })

    timeline_data = [dict(t) for t in set([tuple(d.items()) for d in timeline_data])]
    timeline_data = sorted(timeline_data, key=lambda k: k['time'], reverse=True)

    return timeline_data


def getCommitStatsData(username):
    user = User.objects.filter(username__iexact=username).first()

    if user is None:
        raise Http404("User does not exist")

    commits_count = {}
    commit_data = []

    commits = Commit.objects.filter(project__author=user)
    for c in commits:
        date = c.time.date()
        if date in commits_count:
            commits_count[date] += 1
        else:
            commits_count[date] = 1

    if not commits_count:
        curr_date = datetime.datetime.now().date()
        for i in range(10):
            commit_data.append({"y": str(curr_date), "a": "0"})
            curr_date -= datetime.timedelta(days=1)
        return commit_data

    date = min(commits_count, key=commits_count.get)
    end_date = max(commits_count, key=commits_count.get)

    while date <= end_date:
        if date in commits_count:
            commit_data.append({"y": str(date), "a": str(commits_count[date])})
        else:
            commit_data.append({"y": str(date), "a": "0"})
        date += datetime.timedelta(days=1)

    return commit_data


def getProjectExplorerData(username, projectname, branchname=None):
    user = User.objects.filter(username__iexact=username).first()

    if user is None:
        raise Http404("User does not exist")

    if branchname is None:
        project = Project.objects.filter(name__iexact=projectname).first()
    else:
        project = Project.objects.filter(name__iexact=projectname, branch__iexact=branchname).first()

    if project is None:
        raise Http404("Project does not exist")

    files = File.objects.filter(commit__project=project).order_by('commit__time')
    current_files = {}
    file_data = []

    for f in files:
        if f.size == "0":
            current_files.pop(f.name)
        else:
            current_files[f.name] = {
                "last_commit": f.commit.message,
                "last_commit_time": f.commit.time,
            }

    for key, value in current_files.items():
        file_data.append({
            "name": key,
            "last_commit": value['last_commit'],
            "last_commit_date": value['last_commit_time'].date(),
        })

    latest_commit = max(list(current_files.values()), key=lambda x: x['last_commit_time'])

    commits_count = Commit.objects.filter(project=project).count()
    star_count = Star.objects.filter(project=project).count()
    fork_count = Fork.objects.filter(original_project=project).count()

    branches = []
    all_branches_project = Project.objects.filter(name__iexact=projectname)
    for p in all_branches_project:
        branches.append(p.branch)

    return {
        "name": project.name,
        "branch": project.branch,
        "description": project.description,
        "latest_commit": latest_commit['last_commit'],
        "stars": star_count,
        "forks": fork_count,
        "commits": commits_count,
        "branches": branches,
        "files": file_data,
    }


def getCommitListData(username, projectname, branchname):
    user = User.objects.filter(username__iexact=username).first()

    if user is None:
        raise Http404("User does not exist")

    project = Project.objects.filter(name__iexact=projectname, branch__iexact=branchname).first()

    if project is None:
        raise Http404("Project does not exist")

    commits = Commit.objects.filter(project=project)
    commits_data = {}

    for c in commits:
        date = c.time.date()
        c_data = {
            "author": c.project.author.username,
            "author_img": "images/users/ccd-avatar.jpg",
            "message": c.message,
            "id": c.commit_id,
            "time": c.time
        }
        if date in commits_data:
            commits_data[date].append(c_data)
        else:
            commits_data[date] = [c_data]

    commits_by_date_data = []
    for key in sorted(commits_data, reverse=True):
        cmts = []
        for c in sorted(commits_data[key], key=lambda x: x['time'], reverse=True):
            cmts.append({
                "author": c['author'],
                "author_img": c['author_img'],
                "message": c['message'],
                "id": c['id'],
            })
        commits_by_date_data.append({
            "date": key,
            "commits": cmts,
        })

    return {
        "project": project.name,
        "branch": project.branch,
        "commits_by_date": commits_by_date_data,
    }


def getPrismFileType(filename):
    ext = filename.split('.')[-1].lower()
    name = filename.split('.')[0].lower()

    if name == "makefile":
        return "language-makefile"
    elif ext == "h" or ext == "c":
        return "language-c"
    elif ext == "hpp" or ext == "cpp":
        return "language-cpp"
    elif ext == "py":
        return "language-python"
    elif ext == "java":
        return "language-java"
    elif ext == "js":
        return "language-javascript"
    elif ext == "html":
        return "language-html"
    elif ext == "css":
        return "language-css"
    elif ext == "md":
        return "language-markdown"
    else:
        return "language-"+ext


def getAceFileType(filename):
    ext = filename.split('.')[-1].lower()
    name = filename.split('.')[0].lower()

    if name == "makefile":
        return "makefile"
    elif ext == "h" or ext == "c" or ext == "hpp" or ext == "cpp":
        return "c_cpp"
    elif ext == "py":
        return "python"
    elif ext == "java":
        return "java"
    elif ext == "js":
        return "javascript"
    elif ext == "html":
        return "html"
    elif ext == "css":
        return "css"
    elif ext == "md":
        return "markdown"
    else:
        return ext


def getFileCodeData(username, projectname, branchname, filename):
    user = User.objects.filter(username__iexact=username).first()

    if user is None:
        raise Http404("User does not exist")

    project = Project.objects.filter(name__iexact=projectname, branch__iexact=branchname).first()

    if project is None:
        raise Http404("Project does not exist")

    req_file = File.objects.filter(commit__project=project, name=filename).order_by('-commit__time').first()

    if req_file is None or req_file.size == "0":
        raise Http404("File does not exist")

    return {
        "name": req_file.name,
        "project": project.name,
        "branch": project.branch,
        "size": req_file.size,
        "code": req_file.code,
        "prism_type": getPrismFileType(req_file.name),
        "ace_type": getAceFileType(req_file.name),
    }


def getCommitDiffData(username, projectname, branchname, commitid):
    user = User.objects.filter(username__iexact=username).first()

    if user is None:
        raise Http404("User does not exist")

    project = Project.objects.filter(name__iexact=projectname, branch__iexact=branchname).first()

    if project is None:
        raise Http404("Project does not exist")

    commit = Commit.objects.filter(project=project, commit_id=commitid).first()

    if commit is None:
        raise Http404("Commit does not exist")

    diff_str = ""

    files = File.objects.filter(commit=commit)

    file_set = []
    for f in files:
        prev_files = File.objects.filter(Q(name=f.name) | Q(code=f.code)).order_by('-commit__time')
        for i in range(len(prev_files)):
            if prev_files[i].commit == commit:
                if i+1 >= len(prev_files):
                    file_set.append([None, f])
                else:
                    file_set.append([prev_files[i+1], f])
                break

    for f_p in file_set:
        old_code = "" if f_p[0] is None else f_p[0].code.splitlines()
        new_code = "" if f_p[1].size == "0" else f_p[1].code.splitlines()
        old_file = "/dev/null" if f_p[0] is None else f_p[0].name
        new_file = "/dev/null" if f_p[1].size == "0" else f_p[1].name
        if f_p[0] is None:
            diff_str += "new file mode 100644" + '\n'
        if f_p[1].size == "0":
            diff_str += "deleted file mode 100644" + '\n'
        first_line = True
        for line in difflib.unified_diff(old_code, new_code, fromfile=old_file, tofile=new_file):
            if first_line:
                diff_str += line
                first_line = False
            else:
                diff_str += line + '\n'

    return {
        "project": project.name,
        "branch": project.branch,
        "author": project.author.username,
        "author_img": "images/users/ccd-avatar.jpg",
        "message": commit.message,
        "commit_id": commit.commit_id,
        "date": commit.time,
        "diff": diff_str,
    }