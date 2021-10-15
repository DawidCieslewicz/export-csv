from django.db import transaction
from typing import List, Dict
from blood_tests.models import (
    BloodTestRejected,
    BloodTestsPassed,
    BloodTestsPassedFeedback,
)

# Wiem, że można źle
def blood_test_passed_feedback_create(
    *,
    feedback_list: List[Dict],
    blood_test_passed: BloodTestsPassed,
) -> BloodTestsPassedFeedback:

    for el in feedback_list:
        blood_test_passed_feedback = BloodTestsPassedFeedback(
            feedback_id=el["id"],
            package_code=el["package_code"],
            result_code=el["result_code"],
            description=el.get("description", None),
            blood_test_passed=blood_test_passed,
        )
        blood_test_passed_feedback.full_clean()
        blood_test_passed_feedback.save()

    return blood_test_passed_feedback


@transaction.atomic
def blood_test_passed_create(
    *,
    request_sent: str,
    response_time: int,
    response_http_code: str,
    feedback: List[Dict],
) -> BloodTestsPassed:

    blood_test_passed = BloodTestsPassed(
        request_sent=request_sent,
        response_time=response_time,
        response_http_code=response_http_code,
    )

    blood_test_passed.full_clean()
    blood_test_passed.save()

    blood_test_passed_feedback_create(
        feedback_list=feedback, blood_test_passed=blood_test_passed
    )

    return blood_test_passed


def blood_test_rejected_create(
    *, request_sent: str, response_time: int, error_code: str, response_data: str
) -> BloodTestRejected:
    blood_test_rejected = BloodTestRejected(
        request_sent=request_sent,
        response_time=response_time,
        error_code=error_code,
        response_data=response_data,
    )

    blood_test_rejected.full_clean()
    blood_test_rejected.save()

    return blood_test_rejected
