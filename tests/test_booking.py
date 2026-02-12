import unittest
from unittest.mock import patch

from src.engine import booking


class BookingContextTests(unittest.TestCase):
    def test_record_outcome_appends_timeline(self):
        initial_state = {"events": [{"id": "event-1", "name": "TV"}], "storylines": [], "timeline": []}

        with patch("engine.booking.repository.load_booking_state", return_value=initial_state), patch(
            "engine.booking.repository.save_booking_state"
        ) as save_mock:
            context = booking.MatchBookingContext(event_id="event-1", match_id="match-1", storyline_id=None, belts=["World"])
            context.record_outcome(
                winner=["Hero"],
                loser=["Villain"],
                post_result="Clean Win",
                log="Log output",
                match_type="TV Taping",
            )

        save_mock.assert_called_once()
        saved_state = save_mock.call_args[0][0]
        self.assertEqual(len(saved_state["timeline"]), 1)
        entry = saved_state["timeline"][0]
        self.assertEqual(entry["event_id"], "event-1")
        self.assertEqual(entry["match_id"], "match-1")
        self.assertEqual(entry["winner"], ["Hero"])
        self.assertEqual(entry["loser"], ["Villain"])
        self.assertEqual(entry["belts"], ["World"])


if __name__ == "__main__":
    unittest.main()
