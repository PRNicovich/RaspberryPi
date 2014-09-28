import sys 
import time 
import os.path
import gdata.client, gdata.docs.client, gdata.docs.data, gdata.docs.service
import atom.data
import urllib2
	
class GoogleDriveFileUpload:

	def __init__(self, fileName, targetFolder, username, password, ftype='txt'):
	
		self.fileName = fileName
		self.targetFolder = targetFolder
		self.username = username
		self.password = password
		self.file_type = self.cvtFileType(ftype)
		self.ftype = ftype
		
	
	def cvtFileType(self, ftype):
		if ftype == 'jpg':
			file_type = 'image/jpeg'
		elif ftype == 'kml':
			file_type = 'application/vnd.google-earth.kml+xml'
		elif ftype == 'txt':
			file_type = 'text/plain'
		elif ftype == 'csv':
			file_type = 'text/csv'
		elif ftype == 'mpg':
			file_type = 'audio/mpeg'
		elif ftype == 'mp4':
			file_type = 'video/mp4'
			
		return file_type
		
	def changeFile(self, fileName, ftype = 'txt'):
		self.fileName = fileName
		self.file_type = cvtFileType(ftype)
		self.file_size = os.path.getsize(fhandle.name)
		
	def changeTarget(self, targetFolder):
		self.targetFolder = targetFolder
		
	def upload(self):
		#Start the Google Drive Login
		docsclient = gdata.docs.client.DocsClient(source='GausLabAnalysis')

		# Get a list of all available resources (GetAllResources() requires >= gdata-2.0.15)
		# print 'Logging in...',
		try:
			docsclient.ClientLogin(self.username, self.password, docsclient.source);
		except (gdata.client.BadAuthentication, gdata.client.Error), e:
			sys.exit('Unknown Error: ' + str(e))
		except:
			sys.exit('Login Error. Check username/password credentials.')
		# print 'Success!'

		# The default root collection URI
		uri = 'https://docs.google.com/feeds/upload/create-session/default/private/full'
		# Get a list of all available resources (GetAllResources() requires >= gdata-2.0.15)
		# print 'Fetching Collection/Directory ID...',
		try:
		   resources = docsclient.GetAllResources(uri='https://docs.google.com/feeds/default/private/full/-/folder?title=' + self.targetFolder + '&title-exact=true')
		except:
		   sys.exit('ERROR: Unable to retrieve resources')
		# If no matching resources were found
		if not resources:
		   sys.exit('Error: The collection "' + self.targetFolder + '" was not found.')
		# Set the collection URI
		uri = resources[0].get_resumable_create_media_link().href
		# print 'Success!'
		# Make sure Google doesn't try to do any conversion on the upload (e.g. convert images to documents)
		uri += '?convert=false'

		fhandle = open(self.fileName)
		self.file_size = os.path.getsize(fhandle.name)
		print 'Uploading ', self.fileName,'....' 
		# Create an uploader object and upload the file
		
		# uploader = gdata.client.ResumableUploader(docsclient, fhandle, self.file_type, self.file_size, chunk_size=10485760, desired_class=gdata.data.GDEntry)
		# new_entry = uploader.UploadFile(uri, entry=gdata.data.GDEntry(title=atom.data.Title(text=os.path.basename(fhandle.name))))
		
		mS = gdata.data.MediaSource(content_type = gdata.docs.service.SUPPORTED_FILETYPES[self.ftype.upper()])
		mS.SetFileHandle(self.fileName, self.file_type)
		doc = gdata.docs.data.Resource(type='file', title=os.path.basename(self.fileName))
		doc = docsclient.CreateResource(doc, media=mS, create_uri = uri)

		# print 'Success!',
		print 'File ' + self.fileName + ' uploaded to ' + self.targetFolder + ' at ' + time.strftime("%H:%M:%S %d/%m/%Y ", time.localtime()) + '.'
		

def internet_on():
    try:
        response=urllib2.urlopen('http://74.125.228.100', timeout=5)
        return True
    except:
		return False

def main():
	gdoc = GoogleDriveFileUpload('C:\\Users\\Rusty\\quickstart-python\\document2.txt', 'TemperatureDataRecords', 'GausLabAnalysis', '1LikeB33s')	
	if internet_on():
		gdoc.upload()
	
	
if __name__ == "__main__":
   # stuff only to run when not called via 'import' here
   main()

	
