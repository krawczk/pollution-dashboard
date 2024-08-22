Pollution Data Automated Dashboard
============

The automated pollution data dashboard project aims to provide daily updates on pollution levels in Poland by retrieving data from the GIOS (Chief Inspectorate for Environmental Protection) website. This comprehensive dashboard utilizes various technologies such as pandas, ArcGIS API, ArcGIS Online, ArcGIS Dashboards, GitHub Actions, and GitHub Pages to collect, process, and present pollution data. The primary focus is on monitoring pollutants such as CO, SO2, NO2, and the critical PM2.5 and PM10 particles. The dashboard incorporates predefined thresholds to indicate whether pollution levels in different regions of Poland exceed or remain below the set standards.

Dashboard Link - https://krawczk.github.io/pollution-dashboard/

Dashboard Components:

- Data Source: The GIOS website (https://www.gov.pl/web/gios) serves as the primary data source for the pollution measurements. It provides reliable and up-to-date information on various pollutants across different monitoring stations in Poland.

- Data Retrieval: The automated dashboard employs pandas, a powerful data manipulation library in Python, to retrieve pollution data from the GIOS website. This process is executed daily to ensure the most recent information is available.

- Data Processing: Once the data is retrieved, it undergoes processing to extract relevant information for the dashboard. The pollutants of interest, including CO, SO2, NO2, PM2.5, and PM10, are selected for analysis.

- Thresholds: The dashboard incorporates predefined thresholds for each pollutant to determine whether the pollution levels are within acceptable limits. These thresholds serve as guidelines for assessing air quality and can be adjusted based on regulatory standards or health recommendations.

- Visualization: The ArcGIS API and ArcGIS Online are utilized to create visually appealing and interactive maps, graphs, and charts. These visualizations provide a comprehensive overview of pollution levels across different regions in Poland.

- Dashboard Creation: ArcGIS Dashboards enable the integration of various visual elements into a single dashboard. It allows for customization and layout design, ensuring that the information is presented in a clear and user-friendly manner.

- Automation: GitHub Actions, a feature of the popular code repository platform GitHub, is utilized to automate the data retrieval and processing tasks. This ensures that the dashboard is updated with the latest pollution data on a daily basis.

- Deployment: GitHub Pages serves as the platform for hosting the automated pollution data dashboard. It allows for easy accessibility and sharing of the dashboard with stakeholders and the general public.

Conclusion:
The automated pollution data dashboard project combines the power of data retrieval, processing, visualization, and automation technologies to provide daily updates on pollution levels in Poland. By leveraging the GIOS website as a data source and employing pandas, ArcGIS API, ArcGIS Online, ArcGIS Dashboards, GitHub Actions, and GitHub Pages, this project offers a valuable tool for monitoring air quality and raising awareness about the impact of pollutants. With its interactive and informative visualizations, the dashboard facilitates informed decision-making and promotes a healthier environment for all.
