# insight_project_patent_network
1. The project builds a data warehouse for the patent records from uspto
2. The project provides a web demo for customer to check the connections of their interested patents
3. The project shows the title of one patent you interested in and the other patents citing it (with titles and dates)

![User website](./web.png)

#### Description for scripts
* load_data_into_redshift.py is for cleaning and loading data into aws redshift. 

  (reminder: the port of redshift cluster should be accessable)
  
* seperate_table_into_chunks.py is for cut the long text in description table of patent into several pieces (with user defined number of chunks depended on the length of text)

* app.py is for the front-end website (the below graph).

  The query function 'conn_generate(search_id) is embbed in the app.py for generating the edges and nodes of the connection.
  Another function 'network_graph function' is for plotting the connection of a patent. 

