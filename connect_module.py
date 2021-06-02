from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException

import sys
import os
import time
import random
import requests
 
from PyQt5 import QtCore, QtWidgets, QtGui


#реализация базового класса по работе с Selenium
class SeleniumBaseEngine(QtCore.QObject):

    def __init__(self, mywindow):
        super().__init__()
        self.mywindow = mywindow
        self.chrome_opt = self.mywindow.chrome_opt
        self.browser = self.mywindow.browser

    def close_browser(self):
        self.browser.close()
        self.browser.quit()
    
    #поиск html-элемента по селектору
    def selector_exist(self, selector):
        #browser = self.browser
        try:
            self.browser.find_element_by_css_selector(selector)
            exist = True
        except NoSuchElementException:
            exist = False
        return exist


#класс авторизации в инстаграм, который будет перенесён в другой поток для выполнения кода
class SeleniumWorkerLogin(SeleniumBaseEngine):
    
    def __init__(self, mywindow, username, password):
        super().__init__(mywindow)
        self.username = username
        self.password = password

    selenium_login = QtCore.pyqtSignal(str)

    # метод, который будет выполнять алгоритм в другом потоке
    def login(self):
        browser = self.browser
        browser.get('https://www.instagram.com')
        time.sleep(random.randrange(3, 6))

        username_input = browser.find_element_by_name('username')
        username_input.clear()
        username_input.send_keys(self.username)
        time.sleep(2)

        password_input = browser.find_element_by_name('password')
        password_input.clear()
        password_input.send_keys(self.password)
        password_input.send_keys(Keys.ENTER) #эмуляция нажатия кнопки Enter
        time.sleep(10)
        
        #отображение данных в окне нашего приложения
        if self.selector_exist('#slfErrorAlert'):#если данные неправильные
            self.close_browser()
            self.selenium_login.emit('Вы ввели неправильный логин или пароль!')
        else:#если все хорошо
            self.selenium_login.emit('Вы успешно вошли в аккаунт инстаграм')
            #self.username = username
            #self.password = password
            self.mywindow.ui.lineEdit_2.clear()
            self.mywindow.ui.lineEdit_3.clear()
            #получаем аватар пользователя
            if os.path.exists(f'./{self.username}'):
                print('папка уже существует')
            else:
                os.mkdir(f'./{self.username}')
            img_avatar = '#react-root > section > nav > div._8MQSO.Cx7Bp > div > div > div.ctQZg > div > div:nth-child(5) > span > img'
            img_avatar_src = browser.find_element_by_css_selector(img_avatar).get_attribute('src')
            get_img = requests.get(img_avatar_src)

            with open(f'./{self.username}/{self.username}_avatar_img.jpg', 'wb') as img_file:
                img_file.write(get_img.content)
            self.mywindow.ui.photo.setPixmap(QtGui.QPixmap(f'./{self.username}/{self.username}_avatar_img.jpg'))
            self.mywindow.ui.autorization_button.setEnabled(False)
            self.mywindow.ui.user_name.setText(self.username)


#класс по работе с лайками/скачиванием контента/подписками на пользователей и удалением неподписавшихся
class SeleniumWorkerTask(SeleniumBaseEngine):
    
    def __init__(self, mywindow, username):
        super().__init__(mywindow)
        #self.mywindow = mywindow
        #self.chrome_opt = self.mywindow.chrome_opt
        #self.browser = self.mywindow.browser
        #self.actions = SeleniumInstruments(self)
        self.username = username
        self.posts_urls = []
        self.friends_urls = [] #список хранящий ссылки на подписчиков выбранного пользователя
        self.following_urls = [] #список хранящий ссылки на наши подписки
        self.unfollow_list = [] #список тех, кто на нас не подпислся
        #self.error_userpage_selector = 'main>div>h2._7UhW9'

    selenium_task = QtCore.pyqtSignal(str)#сигнал на вывод системных сообщений в нижней части окна приложения InstDespadesBot.alert_message
    selenium_task_progress = QtCore.pyqtSignal(int)#сигнал на работу прогрессбара InstDespadesBot.progress_value()
    selenium_task_unfollowList = QtCore.pyqtSignal(list)#сигнал на заполнение списка неподписавшихся на нас InstDespadesBot.get_unfollowList()
    selenium_task_clearUnfollowList = QtCore.pyqtSignal()

    def choice_task(self):
        #получаем ссылку из поля ввода
        userpage = self.mywindow.ui.inst_link.text()
        #получаем наш браузер для работы методов 
        web_engine = self.browser

        if len(userpage) > 0 and userpage.find('https://www.instagram.com/') != -1:
            #если выбран чекбокс поставки лайка пользователю
            if self.mywindow.ui.like_check.isChecked():
                self.like_on_user(userpage, web_engine)
            #если чекбокс скачивания контента пользователя
            elif self.mywindow.ui.download_check.isChecked():
                self.download_userpage_content(userpage, web_engine)
            #если чекбокс подписки на подписчиков выбранного пользоваеля
            else: 
                self.get_followers_of_userpage(userpage, web_engine)
        else:
            self.selenium_task.emit('Введите корректную ссылку на инстаграм') 


    def like_on_user(self, userpage, web_engine):
        #browser = self.browser
        self.get_all_userposts_url(userpage, web_engine)
        #browser.get(userpage)
        progress = 0
        time.sleep(4)

        #перебираем ссылки и лайкаем
        if len(self.posts_urls) > 0:
            for post_url in self.posts_urls[0:10]:#для полноценно рабочей версии рабочей срез следует убрать, для тестов используем self.posts_urls[0:10]
                try:
                    web_engine.get(post_url)
                    time.sleep(random.randrange(2, 5))
                    like_button_selector = '.eo2As button.wpO6b'#селектор кнопки лайка
                    web_engine.find_element_by_css_selector(like_button_selector).click()
                    #time.sleep(random.randrange(80, 100))
                    time.sleep(random.randrange(4, 10))
                    self.selenium_task.emit(f'лайк на пост по ссылке {post_url} поставлен!')
                    progress += 100 / len(self.posts_urls)
                    #self.mywindow.ui.progressBar.setValue(progress)
                    self.selenium_task_progress.emit(progress)
                except Exception as ex:
                    self.selenium_task.emit(f'Не удалось поставить лайк {ex}')
                    self.close_browser()
            self.selenium_task.emit(f'работа по функции "поставить лайк" завершена')
        else:
            self.selenium_task.emit('у пользователя нет постов - лайк поставить невозможно')
            self.close_browser()

        #self.close_browser()


    def get_all_userposts_url(self, userpage, web_engine):
        #browser = self.browser
        #browser.get(userpage)
        web_engine.get(userpage)
        time.sleep(4)

        error_userpage_selector = 'main>div>h2._7UhW9'
        if self.selector_exist(error_userpage_selector):
            self.selenium_task.emit('Такого пользователя не существует, проверьте URL')
            self.close_browser()
        else:
            self.selenium_task.emit('Пользователь успешно найден - переходим к дальнейшим действиям')
            time.sleep(2)

            #получаем количество постов
            post_count = int(web_engine.find_element_by_css_selector('header section ul .g47SY:first-child').text)
            loops_count = int(post_count / 12)

            #очищаем список постов, если он содержал какие-то данные
            if len(self.posts_urls) > 0:
                self.posts_urls.clear()
            #прокручиваем страницу и добавляем в массив post_urls ссылки на посты пользователя
            for i in range(0, loops_count):
                hrefs = web_engine.find_elements_by_tag_name('a')
                hrefs = [item.get_attribute('href') for item in hrefs if '/p/' in item.get_attribute('href')]

                for href in hrefs:
                    if href not in self.posts_urls:
                        self.posts_urls.append(href)

                web_engine.execute_script('window.scrollTo(0, document.body.scrollHeight);')
                time.sleep(random.randrange(2, 4))
                self.selenium_task.emit(f'итерация #{i} по получению постов')

            #записываем полученные ссылки в текстовый файл
            file_name = userpage.split('/')[-2]
            with open(f'{file_name}_like_posts.txt', 'w') as file:
                for post_url in self.posts_urls:
                    file.write(post_url + '\n')
            if len(self.posts_urls) > 0:        
                self.selenium_task.emit(f'все посты успешно получены, всего {post_count} поста')
            else:
                self.selenium_task.emit('постов у пользователя не обнаружено')

        
    def download_userpage_content(self, userpage, web_engine):
        #browser = self.browser
        self.get_all_userposts_url(userpage, web_engine)
        file_name = userpage.split('/')[-2]
        #browser.get(userpage)
        time.sleep(4)
        if os.path.exists(f'./{file_name}'):
            self.selenium_task.emit(f'папка уже существует')
        else:
            os.mkdir(f'./{file_name}')

        img_and_video_URL = []
        progress = 0
        #перебираем ссылки и разделяем на фото и видео
        if len(self.posts_urls) > 0:
            for post_url in self.posts_urls:
                try:
                    web_engine.get(post_url)
                    time.sleep(random.randrange(4, 10))
                    img_selector = '.ZyFrc .FFVAD'
                    video_selector = '._5wCQW .tWeCl'
                    post_id = post_url.split('/')[-2]
                    
                    if self.selector_exist(img_selector):
                        img_src = web_engine.find_element_by_css_selector(img_selector).get_attribute('src')
                        img_and_video_URL.append(img_src)

                        #сохранение изображения
                        self.selenium_task.emit(f'сохраняем изображение {post_id}...')
                        get_img = requests.get(img_src)
                        with open(f'./{file_name}/{file_name}_{post_id}_img.jpg', 'wb') as img_file:
                            img_file.write(get_img.content)

                    elif self.actions.selector_exist(video_selector):
                        video_src = web_engine.find_element_by_css_selector(video_selector).get_attribute('src')
                        img_and_video_URL.append(video_src)

                        #сохранение видео
                        self.selenium_task.emit(f'сохраняем видео {post_id}...')
                        get_video = requests.get(video_src, stream = True)
                        with open(f'{file_name}/{file_name}_{post_id}_video.mp4', 'wb') as video_file:
                            for chunk in get_video.iter_content(chunk_size = 1024 * 1024):
                                if chunk:
                                    video_file.write(chunk)
                    else:
                        self.selenium_task.emit(f'Что-то из медиаконтента мы не смогли найти на странице поста {post_url}')
                        img_and_video_URL.append(f'{post_url} селектор неправильный!')
                    self.selenium_task.emit(f'медиафайл из поста {post_url} успешно скачан')
                    progress += 100 / len(self.posts_urls)
                    self.selenium_task_progress.emit(progress)
                except Exception as ex:
                    self.selenium_task.emit(f'Не удалось скачать медиафайл, возникла следующая ошибка {ex}')
                    #self.actions.close_browser()
        else:
            self.selenium_task.emit('у пользователя нет постов - нечего скачивать')
            self.close_browser()

        #self.actions.close_browser()
        
        #записываем массив ссылкок на медиафайлы в текстовый документ
        if len(img_and_video_URL) > 0:
            with open(f'{file_name}/{file_name}_img_and_video_URL.txt', 'a') as file:
                for i in img_and_video_URL:
                    file.write(i + '\n')
            self.selenium_task.emit('функция "скачать контент пользователя" завершила свою работу')
            #self.selenium_task_progress.emit(100)


    def get_followers_of_userpage(self, userpage, web_engine):
        #browser = self.browser
        web_engine.get(userpage)
        time.sleep(4)
        file_name = userpage.split('/')[-2]

        time.sleep(4)
        if os.path.exists(f'./{file_name}'):
            print(f'папка {file_name} уже существует')
        else:
            print(f'Создаем папку пользователя {file_name}')
            os.mkdir(f'./{file_name}')


        if self.selector_exist(self.error_userpage_selector):
            self.selenium_task.emit(f'Пользователя {file_name} не существует, проверьте URL')
            self.close_browser()
        else:
            self.selenium_task.emit(f'Пользователь {file_name} успешно найден - переходим к дальнейшим действиям')
            time.sleep(2)

            followers_button = web_engine.find_element_by_css_selector('header section li a:first-child span')
            followers_count = int(followers_button.text)
            self.selenium_task.emit(f'количество подписчиков пользователя {file_name} - {followers_count}')
            time.sleep(2)

            loops_count = int(followers_count / 12 ) + 1 #12 - число подписчиков пользователя, которое нам выдает одна прокрутка скролла
            self.selenium_task.emit(f'Число итараций по сбору подписчиков: {loops_count}')
            time.sleep(4)

            followers_button.click()
            time.sleep(4)
            #div, родитель ul html-разметки, содержащий список друзей пользователя. именно этот div необходимо скролить
            followers_ul = web_engine.find_element_by_css_selector('div[role=presentation].Yx5HN>div[role=dialog] .isgrP')

            try:
                #скролим список друзей чтобы получить полный список
                for i in range(0, loops_count):
                    web_engine.execute_script('arguments[0].scrollTop = arguments[0].scrollHeight', followers_ul)
                    time.sleep(random.randrange(2, 4))
                    self.selenium_task.emit(f'Итерация #{i}')

                all_urls_div = followers_ul.find_elements_by_tag_name('li')
                #проверка, содержит ли список ссылок на друзей/подписчиков данные, если да то очищаем его
                if len(self.friends_urls) > 0:
                    self.friends_urls.clear()

                #вместо перебора циклом воспользуемся генератором списка, как более производительной реализацией     
                #for url in all_urls_div:
                #    url = url.find_element_by_tag_name('a').get_attribute('href')
                #    if url not in self.friends_urls:
                #        self.friends_urls.append(url)

                self.friends_urls = [url.find_element_by_tag_name('a').get_attribute('href') for url in all_urls_div]

                #сохраняем ссылки на всех подписчиков пользователя в файл
                with open(f'./{file_name}/{file_name}.txt', 'a') as text_file:
                    for link in self.friends_urls:
                        text_file.write(link + '\n')

                #начинаем подписываться на всех подписчиков пользователя
                #print(self.friends_urls)
                progress = 0
                for user in self.friends_urls:
                    try:
                        try:#файл будет хранить ссылки пользователей, на которых мы подписались, если файл не создан - получим соответствующее предупреждение
                            with open(f'./{file_name}/{file_name}_subscribe_list.txt', 'r') as subscribe_list_file:
                                lines = subscribe_list_file.readlines()
                                if user in lines:
                                    self.selenium_task.emit(f'Мы уже подписаны на {user}, переходим к следующему пользователю')
                                    progress += 100 / len(self.friends_urls)
                                    self.selenium_task_progress.emit(progress)
                                    continue
                        except Exception as ex:
                            print('файл со ссылками пользователей, на которых мы подписались, еще не создан')

                        #browser = self.browser
                        web_engine.get(user)
                        page_owner = user.split('/')[-2]
                        time.sleep(random.randrange(4, 6))

                        #если среди подписчиков наша страница, пропускаем ее
                        if self.selector_exist('header section a.sqdOP.L3NKy._8A5w5.ZIAjV'):
                            self.selenium_task.emit(f'Этот  профиль наш  - пропускаем его')
                            progress += 100 / len(self.friends_urls)
                            self.selenium_task_progress.emit(progress)
                        #если мы уже подписались на пользователя
                        elif self.selector_exist('header section button._5f5mN.-fzfL._6VtSN.yZn4P') or self.actions.selector_exist('header section button.sqdOP.L3NKy._8A5w5'):
                            self.selenium_task.emit(f'Уже подписаны на {page_owner} - пропускаем итерацию')
                            progress += 100 / len(self.friends_urls)
                            self.selenium_task_progress.emit(progress)
                            #continue
                        else:#если мы не подписаны на пользователя
                            time.sleep(random.randrange(6, 10))
                            #если аккаунт закрытый
                            if self.selector_exist('main article h2.rkEop'):
                                try:
                                    follow_button = web_engine.find_element_by_css_selector('header section button.sqdOP.L3NKy.y3zKF').click()
                                    self.selenium_task.emit(f'Запросили подписку на закрытый аккаунт {page_owner}')
                                    progress += 100 / len(self.friends_urls)
                                    self.selenium_task_progress.emit(progress)
                                except Exception as ex:
                                    self.selenium_task.emit(f'не удалось подписаться на закрытый аккаунт пользователя {page_owner}. Причина: {ex}')
                            #если открытый аккаунт
                            else:
                                try:
                                    if self.selector_exist('header section button._5f5mN.jIbKX._6VtSN.yZn4P'):
                                        follow_button = web_engine.find_element_by_css_selector('header section button._5f5mN.jIbKX._6VtSN.yZn4P').click()
                                        self.selenium_task.emit(f'Подписались на открытый аккаунт пользователя {page_owner}')
                                        progress += 100 / len(self.friends_urls)
                                        self.selenium_task_progress.emit(progress)

                                    elif self.selector_exist('header section button.sqdOP.L3NKy.y3zKF'):
                                        follow_button = web_engine.find_element_by_css_selector('header section button.sqdOP.L3NKy.y3zKF').click()
                                        self.selenium_task.emit(f'Подписались на открытый аккаунт пользователя {page_owner}')
                                        progress += 100 / len(self.friends_urls)
                                        self.selenium_task_progress.emit(progress)
                                    else:
                                        self.selenium_task.emit(f'Аккаунт пользователя {page_owner} имеет другой селектор кнопки "Подписаться"')
                                        progress += 100 / len(self.friends_urls)
                                        self.selenium_task_progress.emit(progress)
                                        #записываем пользователя, кнопку которого мы не смогли найти по селектору
                                        with open(f'./{file_name}/{file_name}_error_subscribe_list.txt', 'a') as error_subscribe_list_file:
                                            error_subscribe_list_file.write(user + '\n')
                                        continue

                                except Exception as ex:
                                    self.selenium_task.emit(f'При подписке на открытый аккаунт пользователя {page_owner} произошла ошибка: {ex}')

                        #записываем файл, содержащий ссылки на пользователей, на которых мы подписались
                        with open(f'./{file_name}/{file_name}_subscribe_list.txt', 'a') as subscribe_list_file:
                            subscribe_list_file.write(user + '\n')
                        time.sleep(random.randrange(60, 90)) #чтобы не вызывать подозрений, паузу лучше ставить 120-180

                    except Exception as ex:
                        self.selenium_task.emit(f'Не удалось подписаться на пользователя {user}. Причина: {ex}')
                        self.close_browser()

            except Exception as ex:
                self.selenium_task.emit(f'При подписке на подписчиков пользователя {file_name} произошла следующая ошибка: {ex}')
                self.close_browser()

        #self.close_browser()

    #функция обертка для запуска функции ниже
    def start_unsubscribe(self):
        self.unsubscribe_from_unsigned_user(self.username, self.browser)

    #метод формирования списка на отписку от неподписавшивхся на нас в ответ пользователей
    def unsubscribe_from_unsigned_user(self, username, web_engine):
        #browser = self.browser
        web_engine.get(f'https://www.instagram.com/{username}')
        time.sleep(random.randrange(3, 6))
        
        #получаем число наших подписчиков
        followers_button = web_engine.find_element_by_css_selector('header > section > ul > li:nth-child(2) > a > span')
        followers_count = int(followers_button.get_attribute('title').replace(' ', ''))
        
        #получаем число наших подписок
        #following_button = browser.find_element_by_css_selector('header > section > ul > li:nth-child(3) > a')
        #following_count = int(following_button.find_element_by_tag_name('span').text.replace(' ', ''))
        
        self.selenium_task.emit(f'число наших подписчиков: {followers_count}')
        
        followers_loops_count = int(followers_count / 12) + 1
        #following_loops_count = int(following_count / 12) + 1

        #собираем список подписчиков
        followers_button.click()
        time.sleep(4)

        # div хранящий всех подписчиков, который необходимо скролить
        followers_ul = web_engine.find_element_by_css_selector('body > div.RnEpo.Yx5HN > div > div > div.isgrP')

        try:
            progress = 0
            self.selenium_task.emit(f'запускаем сбор наших подписчиков: необходимо провести {followers_loops_count} итераций')
            for i in range(0, followers_loops_count):
                web_engine.execute_script('arguments[0].scrollTop = arguments[0].scrollHeight', followers_ul)
                time.sleep(random.randrange(6, 10))
                self.selenium_task.emit(f'Итерация #{i}')
                progress += 100 / followers_loops_count
                self.selenium_task_progress.emit(progress)

            all_urls_div = followers_ul.find_elements_by_tag_name('li')
            if len(self.friends_urls) > 0:
                self.friends_urls.clear()

            #for url in all_urls_div:
            #    url = url.find_element_by_tag_name('a').get_attribute('href')
            #    self.friends_urls.append(url)
            #заполняем список, хранящий ссылки на наших подписчиков
            self.friends_urls = [url.find_element_by_tag_name('a').get_attribute('href') for url in all_urls_div]

            #сохраняем всех наших подписчиков в файл
            with open(f'{username}_followers_list.txt', 'a') as followers_file:
                for url in self.friends_urls:
                    followers_file.write(url + '\n')
        except Exception as ex:
            self.selenium_task.emit(f'не удалось получить подписчиков пользователя {username}, причина: {ex}')
            self.close_browser()
        time.sleep(random.randrange(4, 6))

        #собираем список подписок пользователя
        #browser = self.browser
        web_engine.get(f'https://www.instagram.com/{username}')
        time.sleep(random.randrange(3, 6))

        following_button = web_engine.find_element_by_css_selector('header > section > ul > li:nth-child(3) > a')
        following_count = int(following_button.find_element_by_tag_name('span').text.replace(' ', ''))
        following_loops_count = int(following_count / 12) + 1

        self.selenium_task.emit(f'число наших подписок: {following_count}')

        following_button.click()
        time.sleep(random.randrange(3, 6))

        following_ul = web_engine.find_element_by_css_selector('body > div.RnEpo.Yx5HN > div > div > div.isgrP')
        try:
            progress = 0
            self.selenium_task.emit(f'запускаем сбор наших подписок: необходимо провести {following_loops_count} итераций')
            for i in range(0, following_loops_count):
                web_engine.execute_script('arguments[0].scrollTop = arguments[0].scrollHeight', following_ul)
                time.sleep(random.randrange(6, 10))
                self.selenium_task.emit(f'Итерация #{i}')
                progress += 100 / following_loops_count
                self.selenium_task_progress.emit(progress)

            all_urls_div = following_ul.find_elements_by_tag_name('li')
            if len(self.following_urls) > 0:
                self.following_urls.clear() 

            #for url in all_urls_div:
            #    url = url.find_element_by_tag_name('a').get_attribute('href')
            #    self.following_urls.append(url)
            #заполняем список наших подписок
            self.following_urls = [url.find_element_by_tag_name('a').get_attribute('href') for url in all_urls_div]

            #сохраняем все наши подписки в файл
            with open(f'{username}_following_list.txt', 'a') as following_file:
                for url in self.following_urls:
                    following_file.write(url + '\n')
        except Exception as ex:
            self.selenium_task.emit(f'не удалось получить подписки пользователя {username}, причина: {ex}')
            self.close_browser()

        #сравниваем списки наших подписчиков и подписок, чтобы создать отдельный список тех, кто на нас не подписался
        #count = 0
        unfollow_list = []
        #for user in self.following_urls:
        #    if user not in self.friends_urls:
        #        count += 1
        #        unfollow_list.append(user)
        unfollow_list = [user for user in self.following_urls if user not in self.friends_urls]
        self.selenium_task.emit(f'нужно  отписаться от {len(unfollow_list)} пользователей')

        #сохраняем всех от кого нужно отписаться в новый файл
        with open(f'{username}_unfollow_list.txt', 'a') as unfollow_file:
            for user in unfollow_list:
                unfollow_file.write(user + '\n')
        self.selenium_task.emit('Запускаем отписку от халтурщиков...')
        time.sleep(2)

        #выводим список ссылок на тех, кто на нас не подписался
        self.selenium_task_unfollowList.emit(unfollow_list)
        #time.sleep(random.randrange(4, 6))
        #self.selenium_task.emit('мы успешно отписались от халтурщиков!')
        #self.close_browser()

    def final_delete_users(self):
        web_engine = self.browser
        progress = 0
        try:
            count = len(self.unfollow_list)
            for user_url in self.unfollow_list:
                user_name_unfollow = user_url.split('/')[-2]
                web_engine.get(user_url)
                time.sleep(random.randrange(4, 6))
                
                #получаем кнопку отписки
                unfollow_button = web_engine.find_element_by_css_selector('header > section > div.nZSzR > div.Igw0E.IwRSH.eGOV_.ybXk5._4EzTm > div > div:nth-child(2) > div > span > span.vBF20._1OSdk > button')
                unfollow_button.click()
                time.sleep(random.randrange(5, 7))

                #подтверждение отписки
                unfollow_button_confirm = web_engine.find_element_by_css_selector('body > div.RnEpo.Yx5HN > div > div > div > div.mt3GC > button.aOOlW.-Cab_')
                unfollow_button_confirm.click()

                self.selenium_task.emit(f'отписались от {user_name_unfollow}')
                progress += 100 / len(self.unfollow_list)
                self.selenium_task_progress.emit(progress)
                count -= 1
                self.selenium_task.emit(f'осталось отписаться от {count} пользователей')
                #time.sleep(random.randrange(120, 130))
                time.sleep(random.randrange(4, 6))
            self.selenium_task_progress.emit(100)
            self.selenium_task.emit(f'завершена работа функции отписки от пользователей')
            self.selenium_task_clearUnfollowList.emit()

        except Exception as ex:
            self.selenium_task.emit(f'не удалось отписаться от пользователя {user_url}, причина: {ex}')
            self.close_browser()

    