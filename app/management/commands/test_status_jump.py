from django.core.management.base import BaseCommand
from app.models import Activity, Organization, NaturalPerson
from app.activity_utils import changeActivityStatus
from datetime import datetime, timedelta


class Command(BaseCommand):
    help = '测试活动状态跳跃修复功能'

    def handle(self, *args, **options):
        self.stdout.write("=== 测试活动状态跳跃修复 ===")

        # 查找一个处于待发布状态的活动
        unpublished_activities = Activity.objects.filter(
            status=Activity.Status.UNPUBLISHED)

        if not unpublished_activities.exists():
            self.stdout.write("没有找到待发布状态的活动，创建测试活动...")

            # 获取一个组织和审核老师
            org = Organization.objects.first()
            teacher = NaturalPerson.objects.first()

            if not org or not teacher:
                self.stdout.write(self.style.ERROR("无法找到组织或教师，跳过测试"))
                return

            # 创建测试活动
            activity = Activity.objects.create(
                title="测试状态跳跃活动",
                organization_id=org,
                examine_teacher=teacher,
                start=datetime.now() + timedelta(hours=2),
                end=datetime.now() + timedelta(hours=3),
                status=Activity.Status.UNPUBLISHED,
                valid=True,
                recorded=True,
                need_apply=False,
                need_checkin=False,
                capacity=10,
                current_participants=0
            )
            self.stdout.write(f"创建测试活动: {activity.id}")
        else:
            activity = unpublished_activities.first()
            self.stdout.write(f"使用现有活动: {activity.id} - {activity.title}")

        self.stdout.write(f"当前状态: {activity.status}")

        # 测试状态跳跃：从待发布直接跳到进行中
        try:
            self.stdout.write("测试：从待发布状态直接跳到进行中状态...")
            changeActivityStatus(
                activity.id, Activity.Status.WAITING, Activity.Status.PROGRESSING)

            # 重新获取活动状态
            activity.refresh_from_db()
            self.stdout.write(f"跳跃后状态: {activity.status}")

            if activity.status == Activity.Status.PROGRESSING:
                self.stdout.write(self.style.SUCCESS("✅ 状态跳跃成功！"))
            else:
                self.stdout.write(self.style.ERROR(
                    f"❌ 状态跳跃失败，当前状态: {activity.status}"))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ 状态跳跃异常: {e}"))

        # 测试状态跳跃：从进行中直接跳到已结束
        try:
            self.stdout.write("测试：从进行中状态直接跳到已结束状态...")
            changeActivityStatus(
                activity.id, Activity.Status.PROGRESSING, Activity.Status.END)

            # 重新获取活动状态
            activity.refresh_from_db()
            self.stdout.write(f"跳跃后状态: {activity.status}")

            if activity.status == Activity.Status.END:
                self.stdout.write(self.style.SUCCESS("✅ 状态跳跃成功！"))
            else:
                self.stdout.write(self.style.ERROR(
                    f"❌ 状态跳跃失败，当前状态: {activity.status}"))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ 状态跳跃异常: {e}"))
