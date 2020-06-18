
import datetime 
from datetime import timedelta
import calendar

class DateHelper:
    @staticmethod
    def add_months(targetDate, months):
        month = targetDate.month - 1 + months
        year =  targetDate.year + (month // 12)
        month = (month % 12) +1
        day = min(targetDate.day,calendar.monthrange(year,month)[1])
        return datetime.date(year,month,day)
    
    @staticmethod
    def to_string(dateValue):
        return dateValue.strftime("%m%d%Y-%H%M%S-%f")
        

