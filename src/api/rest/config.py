from database.project.setup import SetupProjectDatabase

class RequestHeaders:
	PROJECT_DB = "Project-Db"
	DATASETS_DB = "Datasets-Db"
    
	def init(project_db_header, datasets_db_header=None):
		if project_db_header:
			SetupProjectDatabase.init(project_db_header, datasets_db_header)
			return True, ''
		else:
			return False, 'Project database path was not sent in the request header. Please contact the development team.'
		
	def close():
		SetupProjectDatabase.close()