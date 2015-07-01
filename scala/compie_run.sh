
sbt assembly

../spark-1.4.0/bin/spark-submit --class "LDACalc" target/scala-2.10/LDA-assembly-1.0.jar --k $1 ../input-lda
