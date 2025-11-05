from uuid import UUID
from datetime import datetime, timezone
from loguru import logger

from core.services.matching_service import matches_filter, can_send_notification

from apps.worker.app import celery, container
from apps.worker.lifespan import get_loop
from .notify import send_notification


@celery.task(bind=True, max_retries=3)
def match_listing_with_subscriptions(self, listing_id: str):
    """
    Match a listing against active subscriptions and send notifications.

    This task:
    1. Loads the listing from database
    2. Gets all active subscriptions
    3. For each subscription, checks if listing matches filter criteria
    4. Checks rate limiting for each subscription
    5. Queues notification tasks for matching subscriptions
    6. Updates last_sent_at for subscriptions that received notifications

    Args:
        listing_id: UUID of the listing to match
    """
    loop = get_loop()

    async def _match():
        async with container.uow() as uow:
            # Load listing from database
            listing = await uow.listings.get_by_id(UUID(listing_id))
            if not listing:
                logger.warning(f"Listing {listing_id} not found, skipping matching")
                return

            logger.info(f"Matching listing {listing_id} against active subscriptions")

            # Get all active subscriptions
            subscriptions = await uow.subscriptions.get_all_active()

            if not subscriptions:
                logger.info("No active subscriptions found")
                return

            logger.info(f"Found {len(subscriptions)} active subscriptions")

            notifications_queued = 0

            # Match listing against each subscription
            for subscription in subscriptions:
                try:
                    # Load associated filter
                    filter_obj = await uow.filters.get_by_id(subscription.filter_id)
                    if not filter_obj:
                        logger.warning(
                            f"Filter {subscription.filter_id} not found for "
                            f"subscription {subscription.id}"
                        )
                        continue

                    # Check if listing matches filter criteria
                    if not matches_filter(listing, filter_obj):
                        continue

                    # Check rate limiting
                    if not can_send_notification(subscription):
                        logger.debug(
                            f"Subscription {subscription.id} is rate limited, skipping"
                        )
                        continue

                    # Queue notification task
                    send_notification.delay(subscription.chat_id, str(listing.uuid))

                    # Update last_sent_at timestamp
                    subscription.update_last_sent(datetime.now(timezone.utc))
                    await uow.subscriptions.save(subscription)

                    notifications_queued += 1
                    logger.info(
                        f"Queued notification: subscription_id={subscription.id}, "
                        f"chat_id={subscription.chat_id}, listing_id={listing_id}"
                    )

                except Exception as e:
                    logger.error(f"Error matching subscription {subscription.id}: {e}")
                    # Continue with other subscriptions

            # Commit all subscription updates
            await uow.commit()

            logger.success(
                f"Matching completed: listing_id={listing_id}, "
                f"notifications_queued={notifications_queued}"
            )

            return {
                "listing_id": listing_id,
                "total_subscriptions": len(subscriptions),
                "notifications_queued": notifications_queued,
            }

    try:
        result = loop.run_until_complete(_match())
        return result
    except Exception as e:
        logger.error(f"Matching task failed for listing {listing_id}: {e}")
        # Retry the task with exponential backoff
        raise self.retry(exc=e, countdown=60 * (2**self.request.retries))
