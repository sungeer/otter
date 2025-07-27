from viper.model_base import BaseModel


class MessageModel(BaseModel):

    def get_messages(self):
        sql_str = '''
            SELECT 
                id, name, body, is_deleted, create_time, update_time
            FROM 
                message
        '''
        self.conn()
        self.execute(sql_str)
        messages = self.cursor.fetchall()
        self.close()
        return messages
