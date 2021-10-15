from django.db import models


class BloodTestBase(models.Model):
    request_sent = models.TextField()
    timestamp = models.DateTimeField(
        "Czas",
        auto_now_add=True,
    )
    response_time = models.FloatField("Czas odpowiedzi")

    class Meta:
        abstract = True


class BloodTestsPassed(BloodTestBase):
    response_http_code = models.CharField("Kod HTTP odpowiedzi", max_length=3)

    def __str__(self) -> str:
        return f"{self.response_http_code} | {str(self.timestamp)}"

    class Meta:
        verbose_name_plural = "Zatwierdzone testy"
        verbose_name = "Zatwierdzony test"


# Z api otrzymuję liste- zakładam, że może być ich kilka
class BloodTestsPassedFeedback(models.Model):

    RES_CODES = (
        ("A100", "Ok"),
        ("A101", "Indywidualna"),
        ("B100", "Darmowa"),
        ("B101", "Brak dostępności"),
        ("B102", "Brak parametrów"),
        ("B103", "Złe dane"),
        ("B104", "Nieznany błąd"),
        ("B105", "Pacjent niepełnoletni"),
    )

    feedback_id = models.IntegerField("Id Feedbacku z serwera")
    package_code = models.TextField("Kod paczki")
    result_code = models.CharField("Kod wyniku", max_length=20, choices=RES_CODES)
    description = models.TextField("Opis", null=True)
    blood_test_passed = models.ForeignKey(
        BloodTestsPassed, on_delete=models.PROTECT, related_name="feedback"
    )

    def __str__(self) -> str:
        # TODO: Normalize date
        return f"{self.package_code} | {str(self.blood_test_passed.id)}"

    class Meta:
        verbose_name_plural = "Feedbacki"
        verbose_name = "Feedback"


class BloodTestRejected(BloodTestBase):
    error_code = models.CharField("Kod błędu", max_length=20)
    response_data = models.TextField("Odpowiedź z serwera")

    def __str__(self) -> str:
        return f"{self.error_code} | {str(self.timestamp)}"

    class Meta:
        verbose_name_plural = "Odrzucone testy"
        verbose_name = "Odrzucony test"
