import discord
from discord.ext import commands, tasks
import json
import os
from datetime import datetime

class AlarmsCog(commands.Cog):
    """
    Base cog for alarm/reminder functionality.
    Reminders are stored in a JSON file and checked periodically.
    Other cogs can extend this class to add further alarm-related features.
    """
    def __init__(self, bot):
        self.bot = bot
        self.reminder_file = "reminders.json"
        self.reminders = []
        self.load_reminders()
        self.check_reminders.start()

    def load_reminders(self):
        """Load reminders from the JSON file."""
        if os.path.exists(self.reminder_file):
            try:
                with open(self.reminder_file, "r", encoding="utf-8") as f:
                    self.reminders = json.load(f)
            except Exception as e:
                print(f"Error loading reminders: {e}")
                self.reminders = []
        else:
            self.reminders = []

    def save_reminders(self):
        """Save reminders to the JSON file."""
        try:
            with open(self.reminder_file, "w", encoding="utf-8") as f:
                json.dump(self.reminders, f, indent=4)
        except Exception as e:
            print(f"Error saving reminders: {e}")

    def add_reminder(self, user_id: int, time: datetime, message: str):
        """
        Add a reminder to the list and persist it.
        Returns the reminder dict.
        """
        reminder = {
            "id": len(self.reminders) + 1,  # Simple incremental ID
            "user_id": user_id,
            "time": time.isoformat(),
            "message": message
        }
        self.reminders.append(reminder)
        self.save_reminders()
        return reminder

    def delete_reminder(self, reminder_id: int, user_id: int):
        """
        Delete a reminder by its ID for the given user.
        Returns True if deleted, False if not found.
        """
        reminder = next(
            (r for r in self.reminders if r["id"] == reminder_id and r["user_id"] == user_id),
            None
        )
        if reminder:
            self.reminders.remove(reminder)
            self.save_reminders()
            return True
        return False

    def list_user_reminders(self, user_id: int):
        """Return all reminders for a given user."""
        return [r for r in self.reminders if r["user_id"] == user_id]

    @tasks.loop(seconds=30)
    async def check_reminders(self):
        """
        Background task that checks every 30 seconds for any due reminders.
        Sends a DM to the user when a reminder is due.
        """
        now = datetime.utcnow()
        due_reminders = [r for r in self.reminders if datetime.fromisoformat(r["time"]) <= now]
        if due_reminders:
            for reminder in due_reminders:
                user = self.bot.get_user(reminder["user_id"])
                if user:
                    try:
                        await user.send(f"⏰ Reminder: {reminder['message']}")
                    except Exception as e:
                        print(f"Error sending reminder to user {reminder['user_id']}: {e}")
                self.reminders.remove(reminder)
            self.save_reminders()

    @check_reminders.before_loop
    async def before_check_reminders(self):
        await self.bot.wait_until_ready()

    # Commands for setting, listing, and deleting reminders.
    @commands.command(name="setreminder")
    async def set_reminder(self, ctx, time_str: str, *, message: str):
        """
        Sets a reminder.
        Time format: YYYY-MM-DD HH:MM (UTC)
        Example: !setreminder 2025-12-31 23:59 Happy New Year!
        """
        try:
            reminder_time = datetime.strptime(time_str, "%Y-%m-%d %H:%M")
        except ValueError:
            await ctx.send("Time format is incorrect. Use YYYY-MM-DD HH:MM (UTC).")
            return

        reminder = self.add_reminder(ctx.author.id, reminder_time, message)
        await ctx.send(f"Reminder set for {reminder_time} UTC with ID {reminder['id']}.")

    @commands.command(name="listreminders")
    async def list_reminders(self, ctx):
        """Lists your current reminders."""
        user_reminders = self.list_user_reminders(ctx.author.id)
        if not user_reminders:
            await ctx.send("You have no reminders set.")
            return
        response = "Your reminders:\n"
        for r in user_reminders:
            response += f"ID: {r['id']} - Time: {r['time']} - Message: {r['message']}\n"
        await ctx.send(response)

    @commands.command(name="deletereminder")
    async def delete_reminder_command(self, ctx, reminder_id: int):
        """Deletes a reminder by its ID."""
        if self.delete_reminder(reminder_id, ctx.author.id):
            await ctx.send(f"Reminder {reminder_id} deleted.")
        else:
            await ctx.send("Reminder not found.")

def setup(bot):
    bot.add_cog(AlarmsCog(bot))
