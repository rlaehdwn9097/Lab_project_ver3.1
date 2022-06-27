from doctest import testsource
import content as ct
import numpy as np
import random
class Scenario(object):
    def __init__(self,_contentList:list):
        self.contentList=_contentList
    
    def requestGenerate(self,_day):
        titleList = []
        weightList = []
        for i in range(len(self.contentList)):
            titleList.append(self.contentList[i].title)
            howAfter = abs(self.contentList[i].peak_day-_day)
            if howAfter>4:
                howAfter=7-howAfter
            weight = round(gaussian(0,howAfter,2)*self.contentList[i].popularity,4)
            weightList.append(weight)
        choice = random.choices(titleList, weights = weightList, k = 1)
        for i in self.contentList:
            if i.title == choice[0]:
                return i

            
def gaussian(x,mean,sigma):
    return(1/np.sqrt(2*np.pi*sigma**2)) * np.exp(-(x-mean)**2/(2*sigma**2))
emBB =[

#일요일 ###
ct.Content('현재는 아름다워',20,25,0,"drama"),
ct.Content('미운 우리 새끼',20,11.8,0,"comedy"),
ct.Content('태종 이방원',20,11.5,0,"drama"),
ct.Content('1박 2일 시즌4',20,8.4,0,"comedy"),
ct.Content('KBS 뉴스 9',20,8.1,0,"news"),
ct.Content('TV 동물농장',20,7.6,0,"comedy"),
ct.Content('사장님 귀는 당나귀 귀',20,5.6,0,"comedy"),
ct.Content('복면가왕',20,5.6,0,"comedy"),
ct.Content('이슈 Pick, 쌤과 함께',20,5.1,0,"news"),
ct.Content('역사저널 그날',20,5.1,0,"news"),
ct.Content('코로나19 통합뉴스룸',20,5.1,0,"news"),
ct.Content('전국노래자랑',20,4.7,0,"comedy"),
ct.Content('노래가 좋아',20,3.9,0,"comedy"),
ct.Content('집사부 일체',20,3.9,0,"comedy"),
ct.Content('동물의 왕국',20,3.8,0,"news"),

ct.Content('Sunday_news1',20,1.2,0,"news"),
ct.Content('Sunday_news2',20,1.6,0,"news"),
ct.Content('Sunday_news3',20,1.1,0,"news"),
ct.Content('Sunday_comedy1',20,1.3,0,"comedy"),
ct.Content('Sunday_comedy2',20,1.7,0,"comedy"),
ct.Content('Sunday_comedy3',20,1.4,0,"comedy"),
ct.Content('Sunday_drama1',20,1.9,0,"drama"),
ct.Content('Sunday_drama2',20,1.6,0,"drama"),
ct.Content('Sunday_drama3',20,1.2,0,"drama"),

###월요일###
ct.Content('으라차차 내 인생',20,17.1,1,"drama"),
ct.Content('사랑의 꽈배기',20,15.3,1,"drama"),
ct.Content('KBS 뉴스 9',20,10.7,1,"news"),
ct.Content('붉은 단심',20,6.3,1,"drama"),
ct.Content('비밀의 집',20,5.4,1,"drama"),
ct.Content('동상이몽 2',20,4.6,1,"comedy"),
ct.Content('생활의 달인',20,4.6,1,"comedy"),
ct.Content('코로나19 통합뉴스룸',20,10.7,1,"news"),
ct.Content('으라차차 내 인생',20,1.3,1,"drama"),
ct.Content('크레이지 러브',20,1.2,1,"drama"),

ct.Content('Monday_news1',20,1.2,0,"news"),
ct.Content('Monday_news2',20,1.6,0,"news"),
ct.Content('Monday_news3',20,1.1,0,"news"),
ct.Content('Monday_comedy1',20,1.3,0,"comedy"),
ct.Content('Monday_comedy2',20,1.7,0,"comedy"),
ct.Content('Monday_comedy3',20,1.4,0,"comedy"),
ct.Content('Monday_drama1',20,1.9,0,"drama"),
ct.Content('Monday_drama2',20,1.6,0,"drama"),
ct.Content('Monday_drama3',20,1.2,0,"drama"),


##화요일###
ct.Content('으라차차 내 인생',20,16.7,2,"drama"),
ct.Content('사랑의 꽈배기',20,16.3,2,"drama"),
ct.Content('KBS 뉴스 9',20,9.9,2,"drama"),
ct.Content('인간극장',20,9.5,2,"news"),
ct.Content('신발 벗고 돌싱포맨',20,6.4,2,"comedy"),
ct.Content('붉은 단심',20,6.0,2,"drama"),
ct.Content('순간포착 세상에 이런일이',20,5.7,2,"comedy"),
ct.Content('비밀의 집',20,5.3,2,"drama"),
ct.Content('코로나19 통합뉴스룸',20,4.5,2,"news"),


ct.Content('Tuesday_news1',20,1.2,0,"news"),
ct.Content('Tuesday_news2',20,1.6,0,"news"),
ct.Content('Tuesday_news3',20,1.1,0,"news"),
ct.Content('Tuesday_comedy1',20,1.3,0,"comedy"),
ct.Content('Tuesday_comedy2',20,1.7,0,"comedy"),
ct.Content('Tuesday_comedy3',20,1.4,0,"comedy"),
ct.Content('Tuesday_drama1',20,1.9,0,"drama"),
ct.Content('Tuesday_drama2',20,1.6,0,"drama"),
ct.Content('Tuesday_drama3',20,1.2,0,"drama"),

##수요일##
ct.Content('으라차차 내 인생',20,15.7,3,"drama"),
ct.Content('사랑의 꽈배기',20,14.1,3,"drama"),
ct.Content('KBS 뉴스 9',20,9.6,3,"news"),
ct.Content('인간극장',20,9.4,3,"news"),
ct.Content('골 때리는 그녀들',20,7.0,3,"comedy"),
ct.Content('라디오스타',20,5.9,3,"comedy"),
ct.Content('코로나19 통합뉴스룸',20,5.4,3,"news"),
ct.Content('비밀의 집',20,4.9,3,"drama"),
ct.Content('일꾼의 탄생',20,4.9,3,"drama"),
ct.Content('옥탑방의 문제아들',20,3.5,3,"comedy"),

ct.Content('Wednesday_news1',20,1.2,0,"news"),
ct.Content('Wednesday_news2',20,1.6,0,"news"),
ct.Content('Wednesday_news3',20,1.1,0,"news"),
ct.Content('Wednesday_comedy1',20,1.3,0,"comedy"),
ct.Content('Wednesday_comedy2',20,1.7,0,"comedy"),
ct.Content('Wednesday_comedy3',20,1.4,0,"comedy"),
ct.Content('Wednesday_drama1',20,1.9,0,"drama"),
ct.Content('Wednesday_drama2',20,1.6,0,"drama"),
ct.Content('Wednesday_drama3',20,1.2,0,"drama"),

##목요일##
ct.Content('으라차차 내 인생',20,16.2,4,"drama"),
ct.Content('사랑의 꽈배기',20,14.2,4,"drama"),
ct.Content('KBS 뉴스 9',20,10.2,4,"news"),
ct.Content('인간극장',20,8.5,4,"news"),
ct.Content('비밀의 집',20,8.8,4,"drama"),
ct.Content('코로나19 통합뉴스룸',20,4.8,4,"news"),
ct.Content('동물농장',20,4.5,4,"comedy"),
ct.Content('걸어서 세계속으로',20,3.9,4,"news"),

ct.Content('Thursday_news1',20,1.2,0,"news"),
ct.Content('Thursday_news2',20,1.6,0,"news"),
ct.Content('Thursday_news3',20,1.1,0,"news"),
ct.Content('Thursday_comedy1',20,1.3,0,"comedy"),
ct.Content('Thursday_comedy2',20,1.7,0,"comedy"),
ct.Content('Thursday_comedy3',20,1.4,0,"comedy"),
ct.Content('Thursday_drama1',20,1.9,0,"drama"),
ct.Content('Thursday_drama2',20,1.6,0,"drama"),
ct.Content('Thursday_drama3',20,1.2,0,"drama"),

##금요일##
ct.Content('으라차차 내 인생',20,14.7,5,"drama"),
ct.Content('사랑의 꽈배기',20,13.3,5,"drama"),
ct.Content('어게인 마이 라이프',20,10.1,5,"drama"),
ct.Content('인간극장',20,9.6,5,"news"),
ct.Content('KBS 뉴스 9',20,9.4,5,"news"),
ct.Content('나 혼자 산다',20,6.5,5,"comedy"),
ct.Content('비밀의 집',20,5.0,5,"drama"),
ct.Content('코로나19 통합뉴스룸',20,4.8,5,"news"),
ct.Content('자연의 철학자들',20,4.5,5,"news"),

ct.Content('Friday_news1',20,1.2,0,"news"),
ct.Content('Friday_news2',20,1.6,0,"news"),
ct.Content('Friday_news3',20,1.1,0,"news"),
ct.Content('Friday_comedy1',20,1.3,0,"comedy"),
ct.Content('Friday_comedy2',20,1.7,0,"comedy"),
ct.Content('Friday_comedy3',20,1.4,0,"comedy"),
ct.Content('Friday_drama1',20,1.9,0,"drama"),
ct.Content('Friday_drama2',20,1.6,0,"drama"),
ct.Content('Friday_drama3',20,1.2,0,"drama"),

##토요일##
ct.Content('현재는 아름다워',20,20.7,6,"drama"),
ct.Content('어게인 마이 라이프',20,9.6,6,"drama"),
ct.Content('KBS 뉴스 9',20,8.1,6,"news"),
ct.Content('놀면 뭐하니?',20,6.3,6,"comedy"),
ct.Content('불후의 명곡',20,5.7,6,"drama"),
ct.Content('살림하는 남자들 시즌2',20,5.6,6,"comedy"),
ct.Content('시니어 토크쇼 황금연못',20,5.0,6,"comedy"),
ct.Content('코로나19 통합뉴스룸',20,5.0,6,"news"),
ct.Content('전지적 참견 시점',20,4.4,6,"comedy"),

ct.Content('Saturday_news1',20,1.2,0,"news"),
ct.Content('Saturday_news2',20,1.6,0,"news"),
ct.Content('Saturday_news3',20,1.1,0,"news"),
ct.Content('Saturday_comedy1',20,1.3,0,"comedy"),
ct.Content('Saturday_comedy2',20,1.7,0,"comedy"),
ct.Content('Saturday_comedy3',20,1.4,0,"comedy"),
ct.Content('Saturday_drama1',20,1.9,0,"drama"),
ct.Content('Saturday_drama2',20,1.6,0,"drama"),
ct.Content('Saturday_drama3',20,1.2,0,"drama"),

]

emBBScenario = Scenario(emBB)


#testScenario = [ct.Content('a',20),ct.Content('b',20),ct.Content('c',20),ct.Content('d',20),ct.Content('e',20),ct.Content('f',20),ct.Content('g',20),ct.Content('h',20),ct.Content('i',20),ct.Content('j',20)]

testScenario = [ct.Content('a',20,25,1,"drama")]