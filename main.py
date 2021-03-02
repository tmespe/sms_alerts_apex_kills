from apscheduler.schedulers.blocking import BlockingScheduler

scheduler = BlockingScheduler()


@scheduler.scheduled_job("interval", id="main", minutes=1)
def main():
    pass


if __name__ == '__main__':
    main()
