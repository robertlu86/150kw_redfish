import os.path
import traceback
import urllib.request
import getpass
import shutil
from pathlib import Path

class FileUtil:
  @staticmethod
  def read(path):
    f = None
    try:
      f = open(path, "r")
      return f.read()
    except Exception as e:
      # traceback.print_exc()
      print(e)
      raise e
    finally:
      if(f is not None): 
        f.close()
        f = None


  ##
  # Read lines without linefeed characters ("\r\n")
  ##
  @staticmethod
  def readlines(path):
    f = None
    lines = list()
    try:
      f = open(path, "r")
      lines = f.readlines()
      lines = [ line.strip("\r\n") for line in lines ]
      return lines
    except Exception as e:
      # traceback.print_exc()
      print(e)
      raise e
    finally:
      if(f is not None): 
        f.close()
        f = None

  @staticmethod
  def write(text, path):
    f = None
    try:
      last_index = path.rfind("/")
      folder_path = path[:last_index]
      if(not os.path.isdir(folder_path)):
        os.makedirs(folder_path)

      f = open(path, "w")
      f.write(text)
    except Exception as e:
      print(e)
      raise e
    finally:
      if(f is not None): 
        f.close()
        f = None

  @staticmethod
  def exists(path):
    return os.path.exists(path)

  @staticmethod
  def is_file(path):
    return os.path.isfile(path) 

  @staticmethod
  def is_dir(path):
    return os.path.isdir(path) 

  """
  List children of dir
  @param {path} folder path
  @return {List<String>} filenames or dirnames in relative path
  """
  @staticmethod
  def listdir(path):
    return os.listdir(path)

  '''
  List files of dir
  @param {path} folder path
  @return {List<String>} abs path
  '''
  @staticmethod
  def list_files(path):
    ret = []
    for name in os.listdir(path):
      abs_path = os.path.join(path, name)
      if os.path.isfile(abs_path):
        ret.append(abs_path)
      
    return ret

  '''
  List images of dir
  @param {path} folder path
  @return {List<String>} abs path
  '''
  @staticmethod
  def list_images(path):
    ret = []
    for name in os.listdir(path):
      abs_path = os.path.join(path, name)
      if (abs_path.endswith('.jpg') or 
          abs_path.endswith('.jpeg') or 
          abs_path.endswith('.png') or 
          abs_path.endswith('.bmp') or 
          abs_path.endswith('.svg') or 
          abs_path.endswith('.gif') ):
        ret.append(abs_path)
    return ret		


  @staticmethod
  def mkdirs(path):
    os.makedirs(path, exist_ok=True)

  @staticmethod
  def remove_file(path):
    if os.path.exists(path):
      os.remove(path)

  @staticmethod
  def remove_dir(path):
    # os.rmdir(path)
    shutil.rmtree(path)

  @staticmethod
  def download(url, path_to_save):
    last_index = path_to_save.rfind("/")
    folder_path = path_to_save[:last_index]
    
    if(not os.path.isdir(folder_path)):
      os.makedirs(folder_path)

    urllib.request.urlretrieve(url, path_to_save)

  @staticmethod
  def user_home_path():
    # https://stackoverflow.com/questions/4028904/how-to-get-the-home-directory-in-python
    # Python 3.5+
    return str(Path.home())

  @staticmethod
  def username():
    # return getpass.getuser()
    return os.getlogin()

  @staticmethod
  def is_image(path):
    if os.path.isfile(path):
      if path.endswith('.jpg') or path.endswith('.png') or path.endswith('.gif'):
        return True
      else:
        return False
    else:
      return False

	