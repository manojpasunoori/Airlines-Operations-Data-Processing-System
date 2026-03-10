package com.aerostream.analytics.consumer;

import com.aerostream.analytics.service.RouteReliabilityService;
import org.apache.avro.generic.GenericRecord;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.stereotype.Component;

@Component
public class FlightEventConsumer {

    private static final Logger LOGGER = LoggerFactory.getLogger(FlightEventConsumer.class);

    private final RouteReliabilityService reliabilityService;

    public FlightEventConsumer(RouteReliabilityService reliabilityService) {
        this.reliabilityService = reliabilityService;
    }

    @KafkaListener(
            topics = "${aerostream.kafka.topic:flight-events}",
            groupId = "${spring.kafka.consumer.group-id:streaming-analytics-group}"
    )
    public void consume(GenericRecord event) {
        try {
            String origin = valueAsString(event.get("origin"));
            String destination = valueAsString(event.get("destination"));
            if (origin.isBlank() || destination.isBlank()) {
                LOGGER.warn("Skipping event with invalid route payload: {}", event);
                return;
            }

            int delayMinutes = valueAsInt(event.get("delayMinutes"));
            reliabilityService.processFlightEvent(origin, destination, delayMinutes);
        } catch (Exception ex) {
            LOGGER.error("Failed to consume flight event payload: {}", event, ex);
        }
    }

    private String valueAsString(Object value) {
        return value == null ? "" : value.toString();
    }

    private int valueAsInt(Object value) {
        if (value instanceof Number number) {
            return number.intValue();
        }
        return 0;
    }
}
