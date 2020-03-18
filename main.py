from threading import Thread
from threading import Thread

from Config import RunConfig
from TweetsProcessing import TweetsProcessing

from subprocess import call

#
# def thread_second():
#     call(["python", "dashStreamMain.py"])


def main():
    ckey = RunConfig.ckey
    csecret = RunConfig.csecret
    atoken = RunConfig.atoken
    asecret = RunConfig.asecret
    tableName = RunConfig.tableName
    keyWords = RunConfig.keyWords
    for keyWord in keyWords:
        dbName = keyWord[0][1:]+ ".db"
        tweetsProcessing = TweetsProcessing(ckey=ckey,
                                            csecret=csecret, atoken=atoken,
                                            asecret=asecret, dbName=dbName,
                                            tableName=tableName, keyWords=keyWord)

        tweetsProcessing.createTwitterDB()
        tweetsProcessing.run()
        print("Twitter connection success!")

    # #single test
    # dbName = keyWords[0][0][1:] + ".db"
    # tweetsProcessing = TweetsProcessing(ckey=ckey,
    #                                     csecret=csecret, atoken=atoken,
    #                                     asecret=asecret, dbName=dbName,
    #                                     tableName=tableName, keyWords=keyWords[0])
    #
    # tweetsProcessing.createTwitterDB()
    # tweetsProcessing.run()
    # print("Twitter connection success!")
    # #end test

    # processThread = Thread(target=thread_second)  # <- note extra ','
    # processThread.daemon = True
    # processThread.start()
    # print("Create web dash!")


if __name__ == '__main__':
    main()
