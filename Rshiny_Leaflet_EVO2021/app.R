library(shiny)
library(shinyWidgets)
library(dplyr)
library(leaflet)
library(leaflet.extras)
library(stringr)
library(png)
library(shinyjs)
library(DT)
library(visNetwork)
library(rintrojs)
library(shinythemes)
library(shinyauthr)
library(digest)
library(markdown)

recessIcons <- awesomeIconList(
  "Manufacturing" = makeAwesomeIcon(icon = "exclamation", library = "fa",
                                    markerColor = "green"),
  "Cryopreservation" = makeAwesomeIcon(icon = "exclamation", library = "fa",
                                       markerColor = "red")
)

hospitals <- read.csv("treatment_centers.csv")
solutions_test <- read.csv("pareto_front_locations.csv")

hospitals_icon <- makeIcon(
  iconUrl = "hospital_icon.png",
  iconWidth = 20, iconHeight = 20,
  iconAnchorX = 22, iconAnchorY = 22
)

# Create our own custom icons
icons <- pulseIconList(
  "Cryopreservation" = makePulseIcon("cryo_icon.png"),
  "Manufacturing" = makePulseIcon("manu_icon.png"))

# Create our own custom icons
icon_list <- iconList(
  "Cryopreservation" = makeIcon("cryo_icon.png", iconWidth = 24, iconHeight = 30),
  "Manufacturing" = makeIcon("manu_icon.png", iconWidth = 24, iconHeight = 30))

ui <- bootstrapPage(
  theme = shinytheme('journal'),
    tags$style(type = "text/css", "html, body {width:100%;height:100%}"),
    leafletOutput("map", width = "100%", height = "100%"),
    absolutePanel(top = 10, right = 10,
   # sliderInput("speed", "Animation Speed", value = 100, ticks = FALSE, round = 50, min = 50, max = 1000),
    sliderInput(inputId = "solutions", label = "Solutions", 
                min = min(solutions_test$Solution), 
                max = max(solutions_test$Solution),
                value = min(solutions_test$Solution), step = 1,
                animate = T)
                # animate = animationOptions(interval = animation$speed, loop = TRUE)),
    )
  )

server <- function(input, output, session) {
  
  output$map <- renderLeaflet({
    
    x <- solutions_test[solutions_test$Solution %in% input$solutions,]
  
    leaflet() %>% 
      
      addProviderTiles("Stamen.Toner", options =providerTileOptions(noWrap = TRUE)) %>%
      
      addMiniMap(
        tiles = providers$Esri.WorldImagery,
        toggleDisplay = TRUE) %>%
      
      addEasyButton(easyButton(
        icon="fa-globe", title="Zoom to Level 1",
        onClick=JS("function(btn, map){ map.setZoom(1); }"))) %>%
      
      addEasyButton(easyButton(
        icon="fa-crosshairs", title="Locate Me",
        onClick=JS("function(btn, map){ map.locate({setView: true}); }"))) %>%
      
      addDrawToolbar(
        targetGroup = "Editor Style",
        editOptions = editToolbarOptions(
          selectedPathOptions = selectedPathOptions()
        )
      )  %>%
      
      addLayersControl(
        overlayGroups = c("Editor Style"),
        options = layersControlOptions(collapsed = TRUE)
      ) %>%
      addStyleEditor() %>%
      
      addMarkers(data=hospitals,
                 icon = hospitals_icon, 
                 popup = hospitals$Name,) %>%
      
      addEasyButton(easyButton(
        states = list(
          easyButtonState(
            stateName="unfrozen-markers",
            icon="ion-toggle",
            title="Freeze Clusters",
            onClick = JS("
          function(btn, map) {
            var clusterManager =
              map.layerManager.getLayer('cluster', 'quakesCluster');
            clusterManager.freezeAtZoom();
            btn.state('frozen-markers');
          }")
          ),
          easyButtonState(
            stateName="frozen-markers",
            icon="ion-toggle-filled",
            title="UnFreeze Clusters",
            onClick = JS("
          function(btn, map) {
            var clusterManager =
              map.layerManager.getLayer('cluster', 'quakesCluster');
            clusterManager.unfreeze();
            btn.state('unfrozen-markers');
          }")
          )
        )
      )) %>%
      
      addFullscreenControl() %>%
      setView(lat = 39.742, lng = -104.835, zoom = 5) %>%
     # addMarkers(data = hospitals, lng = hospitals$Longitude, lat = hospitals$Latitude, popup = hospitals$Name,
    #                    icon = hospitals_icon) %>%
      addMarkers(data = x, lng = x$Longitude, lat = x$Latitude, icon = icon_list[x$Type])
  })
  
  # update animation interval 
#  animation <- reactiveValues(speed = 100, value = 1)
  
#  observeEvent(input$speed, {
#    invalidateLater(500, session)
    
#    animation$value <- input$slider
#    animation$speed <- input$speed
#  })
  
#  output$displaySpeed <- renderText({
#    HTML("Current interval:", animation$speed)
#  })
  
#  observeEvent(input$speed, {
#    session$sendCustomMessage('resume', TRUE)
#  })
  
#  observeEvent(input$min | input$max, {
#    animation$value <- input$slider
#  })
  
}

shinyApp(ui, server)
