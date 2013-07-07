
import base
import models
from tornado import web, gen


class GroupDashboardHandler(base.BaseHandler):
    @web.asynchronous
    @gen.coroutine
    def get(self):
        user = yield self.get_current_user_async()
        error = self.get_error()
        groups = yield self.execute_thread(models.Group.all_groups)

        self.render(
            'groups_dashboard.html',
            page_title='Groups',
            user=user,
            error=error,
            groups=groups)
        self.tf.send({'groups.dashboard.views': 1}, lambda x: x)

    @base.authenticated_async
    @web.asynchronous
    @gen.coroutine
    def post(self):
        user = yield self.get_current_user_async()
        error = self.get_error()
        name = self.get_argument('name', '')
        url = self.get_argument('url', '').lower()

        if not url or not name:
            self.redirect_msg(
                '/g',
                {'error':
                    'Group name and URL are required to create a group.'})

        if models.Group.url_exists(url):
            self.redirect_msg(
                '/g',
                {'error':
                    'A group with URL \'{}\' already exists, pick another URL and try again.'.format(
                    url)})

        group = models.Group(name=name, url=url)
        group.admins.append(user)
        group.members.append(user)
        group.save()
        self.redirect('/g')

class GroupHandler(base.BaseHandler):
    @web.asynchronous
    @gen.coroutine
    def get(self, url):
        user = yield self.get_current_user_async()
        error = self.get_error()
        url = url.lower()
        group = models.Group.objects(url=url).first()
        members = [u for u in group.members]
        members.sort(reverse=True, key=lambda x: x.yearly_mileage)
        self.render('group.html', page_title=group.name, user=user, group=group, members=members, error=error)
        self.tf.send({'groups.views': 1}, lambda x: x)

    @base.authenticated_async
    @web.asynchronous
    @gen.coroutine
    def post(self, url):
        url = url.lower()
        user = yield self.get_current_user_async()
        error = self.get_error()
        group = models.Group.objects(url=url).first()
        if not user.public:
            self.redirect(group.uri)
        if user in group.members:
            group.members.remove(user)
        else:
            group.members.append(user)
        group.save()
        self.redirect(group.uri)
        self.tf.send({'groups.joins': 1}, lambda x: x)
