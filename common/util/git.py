import os
import shutil
import threading
import time

from git import Repo

gitMutex = threading.Lock()


def cloneRepository(git_url=None, rc_local_path=None, ftp_serv_location: str = '/root/bbb-daemon-repos/'):
    """
        Clone the repository from git to the ftp server!
    :return: (True or False) , (Error message or commit sha of the repo.)
    """
    if type is None:
        print("Not repo URL defined.")
        return False, 'Type is not defined'
    try:
        repo_name = git_url.strip().split('/')[-1].split('.')[0]

        if not git_url.endswith(".git") or (
                not git_url.startswith("http://") and not git_url.startswith("https://")):
            raise Exception("\'{}\' is not a valid git URL.".format(git_url))

        repo_dir = ftp_serv_location + repo_name + "/"
        if os.path.exists(repo_dir) and os.path.isdir(repo_dir):
            shutil.rmtree(repo_dir)
            time.sleep(1)

        repo = Repo.clone_from(url=git_url.strip(), to_path=repo_dir)
        sha = repo.head.object.hexsha
        print('SHA= {}'.format(sha))
        # head.
        ' git rev-parse  HEAD'
        if repo_dir.endswith('/') and rc_local_path.startswith('/'):
            rc_local_path = rc_local_path[1:]
        elif not repo_dir.endswith('/') and not rc_local_path.startswith('/'):
            repo_dir = repo_dir + '/'

        if not os.path.isfile(repo_dir + rc_local_path):
            shutil.rmtree(repo_dir)
            raise Exception("rc.local not found on path.")
        pass

        print('Successfully cloned the repository {} at {}'.format(git_url, repo_dir))
        return True, sha

    except Exception as e:
        print("{}".format(e))
        return False, "{}".format(e)


def checkUrlFunc(git_url=None, rc_local_path=None, callback_func=None):
    """
        Check if the repository is valid !
    :param git_url: git repository url.
    :param rc_local_path: Relative path of the rc.local file including the filename. Root is the repository root
    :param callback_func: Used for pyqt updates.
    :return: (True or False), ("Message")
    """
    if rc_local_path is None or rc_local_path.strip() is None or git_url == "":
        return False, "rc.local is not defined."
    if git_url is None or git_url.strip() is None or git_url == "":
        return False, "URL is not defined."
    if not git_url.endswith(".git") or (not git_url.startswith("http://") and not git_url.startswith("https://")):
        return False, "\'{}\' is not a valid git URL.".format(git_url)

    repo_dir = None
    repo_name = None

    gitMutex.acquire()

    try:

        repo_name = git_url.strip().split('/')[-1].split('.')[0]

        if repo_name is not None:
            repo_dir = os.getcwd() + '/' + repo_name + '/'
            if os.path.exists(repo_dir) and os.path.isdir(repo_dir):
                shutil.rmtree(repo_dir)
                time.sleep(1)

        if repo_name is None or repo_dir is None or os.path.exists(repo_dir):
            gitMutex.release()
            return False, "Error with the cloned directory {}.".format(repo_dir)

        Repo.clone_from(url=git_url.strip(), to_path=repo_dir, progress=callback_func)
        if repo_dir.endswith('/') and rc_local_path.startswith('/'):
            rc_local_path = rc_local_path[1:]
        elif not repo_dir.endswith('/') and not rc_local_path.startswith('/'):
            repo_dir = repo_dir + '/'

        if not os.path.isfile(repo_dir + rc_local_path):
            shutil.rmtree(repo_dir)

            gitMutex.release()
            return False, "rc.local not found on path. Type the full path including the filename. {}".format(
                repo_dir + rc_local_path)
        pass

        shutil.rmtree(repo_dir)
        gitMutex.release()
        return True, "Successfully cloned the repository."
    except Exception as e:
        if repo_name is not None and os.path.exists(repo_dir) and os.path.isdir(repo_dir):
            shutil.rmtree(repo_dir)

        gitMutex.release()
        return False, "Error when cloning the repository. {}.".format(e)
