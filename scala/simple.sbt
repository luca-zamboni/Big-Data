import AssemblyKeys._  // put this at the top of the file

assemblySettings

name := "LDA"

version := "1.0"

scalaVersion := "2.10.4"

libraryDependencies ++= Seq(
  "org.apache.spark"  % "spark-core_2.10"              % "1.4.0" % "provided",
  "org.apache.spark"  % "spark-mllib_2.10"             % "1.4.0" % "provided"
  )
libraryDependencies += "com.github.scopt" %% "scopt" % "3.3.0"
