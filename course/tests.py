from django.contrib.auth.models import Group
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken
from course.models import Course, Lesson, Subscription
from course.serializers import LessonSerializer, CourseSerializer, CourseSubscriptionSerializer
from users.models import User


class LessonAPITestCase(APITestCase):

    def setUp(self) -> None:
        """ Подготовка тестовой базы """

        super().setUp()
        self.user = User.objects.create(
            email='Test@mail.ru',
            is_active=True
        )
        self.user.set_password('123456')
        self.user.save()
        self.access_token = str(RefreshToken.for_user(self.user).access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

        self.course_1 = Course.objects.create(
            name='Test course 1',
            description='1st test course',
            owner=self.user
        )
        self.lesson_1 = Lesson.objects.create(
            name='lesson_test 1',
            description='lesson_test 1',
            course=self.course_1,
            owner=self.user
        )
        self.lesson_2 = Lesson.objects.create(
            name='lesson_test 2',
            description='lesson_test 2',
            course=self.course_1,
            owner=self.user
        )

    def test_create(self):
        """ Тестирование создания урока """

        data = {
            'course': self.course_1.id,
            'name': 'test',
            'description': 'test_add'
        }
        response = self.client.post('/lesson/create/', data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            response.json(),
            {'name': 'test', 'description': 'test_add', 'preview': None,
             'video_url': None, 'course': self.course_1.id, 'owner': self.user.id}
        )

    def test_create_by_moderator(self):
        """ Тестирование создания урока модератором """

        # добавлен и авторизован новый пользователь
        self.mod_user = User.objects.create(
            email='test_moderator@mail.ru',
            is_active=True
        )
        self.mod_user.set_password('654321')
        self.mod_user.save()
        self.access_token = str(RefreshToken.for_user(self.mod_user).access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

        # пользователь добавлен в группу 'moderator'
        self.mod_group = Group.objects.create(name='moderator')
        self.mod_group.user_set.add(self.mod_user)

        data = {
            'course': self.course_1,
            'name': 'Test Lesson Create',
            'description': 'Test add of new lesson by moderator'
        }
        response = self.client.post('/lesson/create/', data=data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_by_owner(self):
        """ Тестирование вывода списка уроков пользователю"""

        # добавлен новый пользователь
        self.new_user = User.objects.create(
            email='New_Test@mail.ru',
            is_active=True
        )
        self.new_user.set_password('258963')
        self.new_user.save()

        # изменён владелец урока на нового пользователя
        self.lesson_1.owner = self.new_user
        self.lesson_1.save()

        # получаем только собственные уроки авторизованного пользователя
        response = self.client.get('/lesson/')
        serializer_data = LessonSerializer([self.lesson_2], many=True).data
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(serializer_data, response.data['results'])
        self.assertEqual(response.data['count'], 1)

    def test_get_by_moderator(self):
        """ Тестирование вывода списка уроков модератору"""

        # добавлен и авторизован пользователь-модератор
        self.mod_user = User.objects.create(
            email='test_moderator@mail.ru',
            is_active=True
        )
        self.mod_user.set_password('654321')
        self.mod_user.save()
        self.access_token = str(RefreshToken.for_user(self.mod_user).access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

        self.mod_group = Group.objects.create(name='moderator')
        self.mod_group.user_set.add(self.mod_user)

        response = self.client.get('/lesson/')
        serializer_data = LessonSerializer([self.lesson_1, self.lesson_2], many=True).data
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(serializer_data, response.data['results'])
        self.assertEqual(2, response.data['count'])

    def test_get_lesson(self):
        """ Тестирование вывода одного урока """

        response = self.client.get(f'/lesson/{self.lesson_1.pk}/')
        serializer_data = LessonSerializer(self.lesson_1).data

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(serializer_data, response.data)

    def test_update(self):
        """ Тестирование изменения урока """

        url = f'/lesson/update/{self.lesson_1.id}/'
        response = self.client.patch(url, {'name': 'new name'})
        self.lesson_1.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.lesson_1.name, 'new name')
        self.assertEqual(self.lesson_1.description, 'lesson_test 1')

    def test_delete(self):
        """ Тестирование удаления урока """

        response = self.client.delete(f'/lesson/delete/{self.lesson_1.id}/')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class CourseAPITestCase(APITestCase):

    def setUp(self) -> None:
        """ Подготовка тестовой базы """

        super().setUp()
        self.user = User.objects.create(
            email='Test_Testov@mail.ru',
            is_active=True
        )
        self.user.set_password('654321')
        self.user.save()
        self.access_token = str(RefreshToken.for_user(self.user).access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

        self.course_1 = Course.objects.create(
            name='Testing course N1',
            description='First test course',
            owner=self.user
        )
        self.course_2 = Course.objects.create(
            name='Testing course N2',
            description='Second test course',
            owner=self.user
        )
        self.subscription = Subscription.objects.create(
            course=self.course_1,
            user=self.user,
            is_active=True
        )

    def test_create(self):
        """ Тестирование создания курса """

        data = {
            'name': 'Test Course Create',
            'description': 'Test of new course add'
        }
        response = self.client.post('/course/', data=data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            response.json(),
            {'name': 'Test Course Create', 'description': 'Test of new course add', 'preview': None,
             'lessons_quantity': 0, 'lessons_list': []}
        )

    def test_create_by_moderator(self):
        """ Тестирование создания курса модератором """

        # добавлен и авторизован новый пользователь
        self.mod_user = User.objects.create(
            email='test_moderator@mail.ru',
            is_active=True
        )
        self.mod_user.set_password('654321')
        self.mod_user.save()
        self.access_token = str(RefreshToken.for_user(self.mod_user).access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

        # пользователь добавлен в группу 'moderator'
        self.mod_group = Group.objects.create(name='moderator')
        self.mod_group.user_set.add(self.mod_user)

        data = {
            'name': 'Test Course Create',
            'description': 'Test add of new course by moderator'
        }
        response = self.client.post('/course/', data=data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_by_owner(self):
        """ Тестирование вывода списка курсов пользователю """

        # добавлен новый пользователь
        self.new_user = User.objects.create(
            email='New_Test@mail.ru',
            is_active=True
        )
        self.new_user.set_password('258963')
        self.new_user.save()

        # изменён владелец курса на нового пользователя
        self.course_1.owner = self.new_user
        self.course_1.save()

        # получен только собственный курс авторизованного пользователя
        response = self.client.get('/course/')
        serializer_data = CourseSerializer([self.course_2], many=True).data
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'], serializer_data)
        self.assertEqual(response.data['count'], 1)

    def test_get_by_moderator(self):
        """ Тестирование вывода списка курсов модератору"""

        # добавлен и авторизован новый пользователь
        self.mod_user = User.objects.create(
            email='test_moderator@mail.ru',
            is_active=True
        )
        self.mod_user.set_password('654321')
        self.mod_user.save()
        self.access_token = str(RefreshToken.for_user(self.mod_user).access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

        # пользователь добавлен в группу 'moderator'
        self.mod_group = Group.objects.create(name='moderator')
        self.mod_group.user_set.add(self.mod_user)

        response = self.client.get('/course/')
        serializer_data = CourseSerializer([self.course_1, self.course_2], many=True).data
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'], serializer_data)
        self.assertEqual(response.data['count'], 2)

    def test_get_course(self):
        """ Тестирование вывода одного курса """

        response = self.client.get(f'/course/{self.course_1.pk}/')
        serializer_data = CourseSubscriptionSerializer(self.course_1).data

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer_data)

    def test_update(self):
        """ Тестирование изменения курса """

        url = f'/course/{self.course_1.id}/'
        response = self.client.patch(url, {'name': 'new name'})
        self.course_1.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.course_1.name, 'new name')
        self.assertEqual(self.course_1.description, 'First test course')

    def test_delete(self):
        """ Тестирование удаления курса """

        response = self.client.delete(f'/course/{self.course_1.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_create_subscription(self):
        """ Тестирование создания подписки на курс """

        url = f'/subscribe/{self.course_2.id}/'
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Subscription.objects.filter(course_id=self.course_2.id, user_id=self.user.id, is_active=True))
        self.assertEqual(response.json(), ['Вы подписались на обновления курса.'])

    def test_create_existing_subscription(self):
        """ Тестирование ошибочного создания существующей подписки """

        url = f'/subscribe/{self.course_1.id}/'
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), ['Вы уже подписаны на обновления курса.'])

    def test_subscription_recovery(self):
        """ Тестирование восстановления подписки """

        self.subscription.is_active = False
        self.subscription.save()
        response = self.client.post(f'/subscribe/{self.course_1.id}/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), ['Вы вновь подписались на обновления курса.'])

    def test_delete_subscription(self):
        """ Тестирование удаления подписки """

        response = self.client.delete(f'/subscription/delete/{self.course_1.id}/')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Subscription.objects.filter(course_id=self.course_1.id, user_id=self.user.id, is_active=True))
