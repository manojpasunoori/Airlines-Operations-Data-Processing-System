package com.aerostream.analytics.consumer;

import com.aerostream.analytics.service.RouteReliabilityService;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.stereotype.Component;

@Component
public class FlightEventConsumer {

    private static final Logger LOGGER = LoggerFactory.getLogger(FlightEventConsumer.class);

    private final ObjectMapper objectMapper;
    private final RouteReliabilityService reliabilityService;

    public FlightEventConsumer(ObjectMapper objectMapper, RouteReliabilityService reliabilityService) {
        this.objectMapper = objectMapper;
        this.reliabilityService = reliabilityService;
    }

    @KafkaListener(
            topics = "${aerostream.kafka.topic:flight-events}",
            groupId = "${spring.kafka.consumer.group-id:streaming-analytics-group}"
    )
    public void consume(String payload) {
        try {
            JsonNode event = objectMapper.readTree(payload);
            String origin = event.path("origin").asText("");
            String destination = event.path("destination").asText("");
            if (origin.isBlank() || destination.isBlank()) {
                LOGGER.warn("Skipping event with invalid route payload: {}", payload);
                return;
            }

            int delayMinutes = event.path("delay_minutes").asInt(0);
            reliabilityService.processFlightEvent(origin, destination, delayMinutes);
        } catch (Exception ex) {
            LOGGER.error("Failed to consume flight event payload: {}", payload, ex);
        }
    }
}
