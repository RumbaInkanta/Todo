from datetime import date
 
now = date.fromisoformat('20191204')
print(now)
deadline = date(2017, 5, 22)
if now > deadline:
    print("Срок выполнения прошел")
elif now.day == deadline.day and now.month == deadline.month and now.year == deadline.year:
    print("Срок выполнения сегодня")
else:
    period = deadline - now
    print("Осталось {} дней".format(period.days))